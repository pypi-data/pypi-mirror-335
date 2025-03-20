import logging
from asyncio import run
from enum import StrEnum
from tg_auth import UserStatus
from x_model import init_db, HTTPException, FailReason
from xync_client.TgWallet.ex import ExClient
from xync_schema import models

from xync_client.TgWallet.pyd import (
    CredEpyd,
    Attrs,
    AttrsV2,
    OneAdTakerMakerSale,
    OneAdMakerBuy,
    AdMakerBuy,
    AdMakerSale,
    AdMakerNewSale,
    _AdNew,
    FiatEpydIn,
    _PmsTrait,
    OneAdTakerBuy,
    OrderEpyd,
    AdMakerNewBuy,
    OrderEpydIn,
    AvailableVolume,
)
from xync_client.loader import PG_DSN
from xync_schema.enums import AdStatus

from xync_client.Abc.Base import ListOfDicts
from xync_client.TgWallet.auth import AuthClient
from xync_schema.models import (
    Cur,
    Coin,
    OrderStatus,
    Pmex,
    Fiat,
    Ad,
    Pmcur,
    Cred,
    Agent,
    Curex,
    Coinex,
    Pm,
    Order,
    Actor,
)
from xync_schema.pydantic import FiatNew, BaseAdPydIn, AdBuyPydIn, AdSalePydIn, CredPydIn, OrderPydIn

from xync_client.Abc.Agent import BaseAgentClient


class Exceptions(StrEnum):
    ORDER_KYC = "FIAT_COUNTRY_NOT_SUPPORTED_BY_USER_KYC_COUNTRY"
    PM_KYC = "OFFER_FIAT_COUNTRY_NOT_SUPPORTED_BY_USER_KYC_COUNTRY"
    ROUND = "ROUNDING_IS_NOT_SUPPORTED"
    CUR = "CURRENCY_IS_NOT_SUPPORTED_BY_PAYMENT_METHOD"
    MAX_ADS = "ACTIVE_OFFER_COUNT_LIMIT_REACHED"
    INACTIVE_AD = "OFFER_ILLEGAL_STATE"


# class Status(IntEnum):
#     ALL_ACTIVE = OrderStatus.active


class AgentClient(BaseAgentClient, AuthClient):
    ex_client: ExClient

    # 0: Получение ордеров в статусе status, по монете coin, в валюте coin, в направлении is_sell
    async def orders(
        self, status: OrderStatus = OrderStatus.created, coin: Coin = None, cur: Cur = None, is_sell: bool = None
    ) -> ListOfDicts:
        order = await self._post(
            "/p2p/public-api/v2/offer/order/history/get-by-user-id",
            {"offset": 0, "limit": 100, "filter": {"status": "ALL_ACTIVE"}},  # "limit": 20
        )
        return order["data"]

    # 0: Получение ордера по ид
    async def order(self, oid) -> ListOfDicts:
        orders = await self._post("/p2p/public-api/v2/offer/order/get", {"orderId": oid})
        return orders["data"]

    async def order_ad2epydin(self, ad: Ad, amount: float, cred_id: int = None) -> OrderEpydIn:
        if not cred_id:  # i am taker
            iam_maker = self.agent.actor_id == ad.maker_id
            iam_seller = ad.direction.sell == iam_maker
            cred_filter = (
                {"actor__agent__user_id": self.agent.user_id}
                if iam_seller
                else {  # its a buy ad, i am taker
                    "actor": ad.maker
                }
            )
            await Cred.filter(
                **cred_filter,
                pmcur__pms__in=ad.pms,
                # todo: ordering and filtering by fiat.amount-target
            ).first() if iam_seller else 0
        await ad.fetch_related("direction__pairex__pair__cur")
        return OrderEpydIn(
            offerId=ad.exid,
            amount=AvailableVolume(currencyCode=ad.direction.pairex.pair.cur.ticker, amount=str(int(amount))),
            type="SALE" if ad.direction.sell else "PURCHASE",
            paymentDetailsId=cred_id,
        )

    # 1: [T] Запрос на старт сделки
    async def order_request(self, req: OrderEpydIn) -> OrderEpyd | dict:
        request = await self._post("/p2p/public-api/v2/offer/order/create-by-amount", req.model_dump(exclude_none=True))
        if r := request.get("data"):
            res = await self._post("/p2p/public-api/v2/offer/order/confirm", {"orderId": r["id"], "type": req.type})
            if res.get("status") == "SUCCESS":
                return OrderEpyd(**r)
        logging.error(request)
        return request

    async def order_epyd2pydin(self, order: OrderEpyd) -> OrderPydIn:
        ad = await Ad.get(exid=order.offerId, direction__pairex__ex=self.ex)
        cred = await Cred.get(exid=order.paymentDetails.id, actor__ex=self.ex)
        iam_maker = self.agent.actor == ad.maker
        taker = (
            (await Actor.get(exid=(order.seller if order.is_sell == iam_maker else order.buyer).userId, ex=self.ex))
            if iam_maker
            else self.agent.actor
        )
        return OrderPydIn(
            exid=order.id,
            amount=order.amount.amount,
            maker_topic=None,
            taker_topic=None,
            status=OrderStatus.created,
            created_at=order.createDateTime,
            payed_at=None,
            confirmed_at=None,
            appealed_at=None,
            ad=ad,
            cred=cred,
            taker=taker,
        )

    @staticmethod
    async def order_pydin2db(order: OrderPydIn) -> Order:
        df, unq = order.args()
        order_db, _ = await Order.update_or_create(df, **unq)
        return order_db

    # # # FIATS # # #
    def fiat_args2ex_pyd(
        self, exid: int | str, cur: str, detail: str, name: str, fid: int, typ: str, extra=None
    ) -> CredEpyd:
        fiat = self.fiat_pyd(
            paymentMethodCode=exid,
            currencyCode=cur,
            name=name,
            attributes=Attrs(
                version=typ,
                values=[Attrs.KeyVal(name={"V1": "PAYMENT_DETAILS_NUMBER", "V2": "PHONE"}[typ], value=detail)],
            ),
        )
        if typ == "V2":
            assert issubclass(extra, list) and extra, "extra should not be empty on V2 type"
            fiat.attributes.values.append(
                AttrsV2.KeyVal(
                    name="BANKS",
                    value=extra,  # ["bank1", "bank2"]
                )
            )
        return fiat

    @staticmethod
    def fiat_args2upsert(exid: int | str, cur: str, detail: str, name: str, fid: int = None) -> dict:
        return {
            **({"id": fid} if fid else {}),
            "paymentMethodCode": exid,
            "currencyCode": cur,
            "name": name,
            "attributes": {"version": "V1", "values": [{"name": "PAYMENT_DETAILS_NUMBER", "value": detail}]},
        }

    # 25: Список реквизитов моих платежных методов
    async def creds(self) -> list[CredEpyd]:
        resp = await self._post("/p2p/public-api/v3/payment-details/get/by-user-id")
        return [CredEpyd(**fiat) for fiat in resp["data"]]

    async def cred_epyd2pydin(self, fiat: CredEpyd) -> CredPydIn:
        if not (pmex := await Pmex.get_or_none(exid=fiat.paymentMethod.code, ex=self.ex_client.ex)):
            raise HTTPException(
                FailReason.body, f"No Pmex {fiat.paymentMethod.code} on ex#{self.ex_client.ex.name}", 404
            )
        if not (pmcur := await Pmcur.get_or_none(cur__ticker=fiat.currency, pm_id=pmex.pm_id)):
            raise HTTPException(
                FailReason.body, f"No Pmcur with cur#{fiat.currency} and pm#{fiat.paymentMethod.code}", 404
            )
        ch = self.agent.actor.ch_id
        cred_pin = CredPydIn(
            exid=fiat.id,
            pmcur=pmcur,
            ch=ch,
            name=fiat.name,
        )
        for val in fiat.attributes.values:
            if val.name == "BANKS":
                cred_pin.banks = [b.code for b in val.value]
            else:
                cred_pin.detail = val.value
        return cred_pin

    # 25: Список реквизитов моих платежных методов
    async def set_fiats(self) -> list[Fiat]:
        creds_epyd: list[CredEpyd] = await self.creds()
        creds_pyd_in: list[CredPydIn] = [await self.cred_epyd2pydin(f) for f in creds_epyd]
        creds_db = [await self.cred_pydin2db(crd) for crd in creds_pyd_in]
        fiats_db = [await self.fiat_cred2db(cd) for cd in creds_db]
        return fiats_db

    # 26: Создание реквизита моего платежного метода
    async def fiat_new(self, fiat: FiatNew) -> Fiat:
        pmex = await Pmex.get(pm_id=fiat.pm_id, ex=self.ex_client.ex).prefetch_related("pm")
        cur = await Cur[fiat.cur_id]
        vals = (
            [{"name": "PAYMENT_DETAILS_NUMBER", "value": fiat.detail}]
            if fiat.banks
            else [{"name": "PHONE", "value": fiat.detail}, {"name": "BANKS", "value": fiat.banks}]
        )
        fiat_in = FiatEpydIn(
            paymentMethodCode=pmex.exid,
            currencyCode=cur.ticker,
            name=fiat.name,
            attributes={"values": vals},
        )
        add_fiat = await self._post("/p2p/public-api/v3/payment-details/create", fiat_in.model_dump())
        CredEpyd(**add_fiat["data"])
        cred, _ = await Cred.update_or_create(
            {"name": fiat.name, "detail": fiat.detail}, ex=self.ex_client.ex, exid=add_fiat["data"]["id"]
        )
        fiat_db, _ = await Fiat.update_or_create({"amount": fiat.amount, "target": fiat.target}, cred=cred)

        pmex = await Pmex.get(exid=add_fiat["data"]["paymentMethod"]["code"], ex=self.ex_client.ex)
        cur = await Cur.get(ticker=add_fiat["data"]["currency"])
        pmcur, _ = await Pmcur.get_or_create(cur=cur, pm_id=pmex.pm_id)
        attrs = {a["name"]: a["value"] for a in add_fiat["data"]["attributes"]["values"]}
        f, _ = await Fiat.update_or_create(
            {"detail": attrs["PAYMENT_DETAILS_NUMBER"]}, pmcur=pmcur, user_id=self.agent.user_id
        )
        return f

    # 27: Редактирование реквизита моего платежного метода
    async def fiat_upd(self, fiat_id: int, detail: str, name: str = None) -> Fiat:
        fiat = await Fiat.get(fiatexs__exid=fiat_id, fiatexs__ex=self.ex_client.ex).prefetch_related("pmcur")
        pmex = await Pmex.get(pm_id=fiat.pmcur.pm_id, ex=self.ex_client.ex)
        cur = await Cur[fiat.pmcur.cur_id]
        edit_fiat = await self._post(
            "/p2p/public-api/v3/payment-details/edit",
            {
                "id": fiat_id,
                "paymentMethodCode": pmex.exid,
                "currencyCode": cur.ticker,
                "name": name,
                "attributes": {"version": "V1", "values": [{"name": "PAYMENT_DETAILS_NUMBER", "value": detail}]},
            },
        )
        pmex = await Pmex.get(exid=edit_fiat["data"]["paymentMethod"]["code"], ex=self.ex_client.ex)
        cur = await Cur.get(ticker=edit_fiat["data"]["currency"])
        pmcur, _ = await Pmcur.get_or_create(cur=cur, pm_id=pmex.pm_id)
        attrs = {a["name"]: a["value"] for a in edit_fiat["data"]["attributes"]["values"]}
        f, _ = await Fiat.update_or_create(
            {"detail": attrs["PAYMENT_DETAILS_NUMBER"]}, pmcur=pmcur, user_id=self.agent.user_id
        )
        await Cred.update_or_create({"exid": edit_fiat["data"]["id"]}, ex=self.ex_client.ex, fiat=f)
        return f

    # 28: Удаление реквизита моего платежного метода
    async def fiat_del(self, fiat_id: int) -> bool:
        del_fiat = await self._post("/p2p/public-api/v3/payment-details/delete", {"id": fiat_id})
        return del_fiat

    async def ad_epyd2pydin(self, ad_: OneAdTakerMakerSale | OneAdMakerBuy | OneAdTakerBuy) -> AdBuyPydIn | AdSalePydIn:
        ad_in: BaseAdPydIn = await self.ex_client.ad_common_epyd2pydin(ad_)
        ad_in.maker = self.agent.actor
        if isinstance(ad_, _PmsTrait):
            return AdBuyPydIn(
                **ad_in.model_dump(),
                pms_=await Pm.filter(pmexs__ex=self.ex_client.ex, pmexs__exid__in=[p.code for p in ad_.paymentMethods]),
            )
        creds_pin: list[CredPydIn] = [await self.cred_epyd2pydin(c) for c in ad_.paymentDetails]
        creds_ = [(await Cred.update_or_create((a := cp.args())[0], **a[1]))[0] for cp in creds_pin]
        return AdSalePydIn(**ad_in.model_dump(), creds_=creds_)

    # 29: Список моих объявлений
    async def my_ads(self, status: AdStatus = None) -> list[AdMakerBuy | AdMakerSale]:
        def model(ad: dict) -> (AdMakerBuy | AdMakerSale).__class__:
            return AdMakerSale if ad["type"] == "SALE" else AdMakerBuy

        mapping = {AdStatus.defActive: "INACTIVE", AdStatus.active: "ACTIVE"}
        ads = await self._post(
            "/p2p/public-api/v2/offer/user-own/list",
            {"offset": 0, "limit": 20},  # , "offerType": "SALE"|"PURCHASE"
        )
        return [model(ad)(**ad) for ad in ads["data"] if not status or (status and ad["status"] == mapping[status])]

    # 43: Моя объява по id
    async def my_ad(self, ad_id: int) -> OneAdMakerBuy | OneAdTakerMakerSale:
        ad = await self._post("/p2p/public-api/v2/offer/get-user-own", {"offerId": ad_id})
        ad: dict = ad["data"]
        assert ad["user"]["userId"] == self.agent.actor.exid, "Not your ad"
        model = OneAdTakerMakerSale if ad["type"] == "SALE" else OneAdMakerBuy
        return model(**ad)

    async def ad_f2ein(
        self, coin: Coin, cur: Cur, is_sell: bool, vol: int = None, cur_min: int = None
    ) -> AdMakerNewSale | AdMakerNewBuy:
        coinex = await Coinex.get(coin=coin, ex=self.ex)
        curex = await Curex.get(ex=self.ex, cur=cur)
        creds = await Cred.filter(ch__actor__agent__user_id=self.agent.user_id, pmcur__cur=cur).limit(5)
        # todo: ordering and filtering by fiat.amount-target
        ad_ein = _AdNew(
            type="SALE" if is_sell else "PURCHASE",
            initVolume=AvailableVolume(currencyCode=coinex.exid, amount=str(vol or coinex.minimum)),
            orderRoundingRequired=curex.rounding_scale is not None,
            price={
                "type": "FLOATING",
                "baseCurrencyCode": coinex.exid,
                "quoteCurrencyCode": curex.exid,
                "value": "120" if is_sell else "80",
            },
            orderAmountLimits={"min": str(cur_min or curex.minimum)},
            paymentConfirmTimeout="PT15M",
            comment="tst",
        )
        if ad_ein.type == "SALE":
            ad_ein = AdMakerNewSale(**ad_ein.model_dump(exclude_none=True), paymentDetailsIds=[c.exid for c in creds])
        else:
            pmexs = await Pmex.filter(ex=self.agent.actor.ex, pm__pmcurs__id__in=[c.pmcur_id for c in creds])
            ad_ein = AdMakerNewBuy(**ad_ein.model_dump(exclude_none=True), paymentMethodCodes=[p.exid for p in pmexs])
        return ad_ein

    # 30: Создание объявления
    async def ad_new(self, ad: _AdNew) -> OneAdMakerBuy | OneAdTakerMakerSale:
        create = await self._post("/p2p/public-api/v2/offer/create", ad.model_dump())
        if res := create.get("data"):
            return OneAdTakerMakerSale(**res) if res["type"] == "SALE" else OneAdMakerBuy(**res)
        raise Exception(create)

    # 31: Редактирование объявления
    async def ad_upd(
        self,
        offer_id: int,
        amount: int,
        fiats: list[Fiat] = None,
        price: float = None,
        is_float: bool = None,
        min_fiat: int = None,
        details: str = None,
        autoreply: str = None,
        status: AdStatus = None,
    ) -> Ad.pyd():
        ad = await self.my_ad(offer_id)

        upd = await self._post(
            "/p2p/public-api/v2/offer/edit",
            {
                "offerId": offer_id,
                "paymentConfirmTimeout": ad["paymentConfirmTimeout"],
                "type": ad["type"],
                "orderRoundingRequired": False,
                "price": {"type": "FIXED", "value": ad["price"]["value"]},
                "orderAmountLimits": {"min": ad["orderAmountLimits"]["min"]},
                "comment": "",  # TODO: comment
                "volume": f"{amount}",
                "paymentDetailsIds": [a["id"] for a in ad["paymentDetails"]],
            },
        )
        return upd

    # 32: Удаление
    async def ad_del(self, offer_id: int) -> bool:
        ad = await self.my_ad(offer_id)
        ad_del = await self._post("/p2p/public-api/v2/offer/delete", {"type": ad["type"], "offerId": offer_id})
        return ad_del["status"] == "SUCCESS"

    # 33: Вкл/выкл объявления
    async def ad_switch(self, ad_id: int, active: bool) -> bool:
        ad: OneAdMakerBuy | OneAdTakerMakerSale = await self.my_ad(ad_id)
        pre = "" if active else "de"
        switch = await self._post(f"/p2p/public-api/v2/offer/{pre}activate", {"type": ad.type, "offerId": ad_id})
        return switch["status"] == "SUCCESS"

    # 34: Вкл/выкл всех объявлений
    async def ads_switch(self, active: bool) -> bool:
        pre = "enable" if active else "disable"
        switch = await self._post(f"/p2p/public-api/v2/user-settings/{pre}-bidding")
        return switch["status"] == "SUCCESS"

    # 35: Получить объект юзера по его ид
    async def get_user(self, user_id: int = None, offer_id: int = None) -> dict:
        user = await self._post("/p2p/public-api/v2/offer/get", {"offerId": offer_id})
        return user["data"]["user"]

    # 36: Отправка сообщения юзеру с приложенным файлом
    async def send_user_msg(self, msg: str, file=None) -> bool:
        pass

    # 37: (Раз)Блокировать юзера
    async def block_user(self, is_blocked: bool = True) -> bool:
        return None

    # 38: Поставить отзыв юзеру
    async def rate_user(self, positive: bool) -> bool:
        return None

    # base_url = 'https://p2p.walletbot.me'
    # middle_url = '/p2p/'

    # 19 - order_paid
    async def order_paid(self, order_id: str, file: dict):
        paid = await self._post(
            "/p2p/public-api/v2/offer/order/confirm-sending-payment", {"orderId": order_id, "paymentReceipt": file}
        )
        return paid


async def main():
    await init_db(PG_DSN, models, True)
    maker: Agent
    taker: Agent
    maker, taker = (
        await Agent.filter(actor__ex_id=34, auth__isnull=False, user__status__gte=UserStatus.MEMBER)
        .order_by("user_id")
        .limit(2)
        .prefetch_related("actor__ex")
    )
    mcl: AgentClient = maker.client()
    tcl: AgentClient = taker.client()
    await tcl.set_fiats()
    await mcl.set_fiats()
    my_ads = await mcl.my_ads()
    my_ads_in = [await mcl.ad_epyd2pydin(ma) for ma in my_ads]
    _my_ads_db = [await mcl.ad_pydin2db(ma) for ma in my_ads_in]

    coin = await Coin.get(ticker="USDT")
    cur = await Cur.get(ticker="RUB")
    ad_sell_ein = await tcl.ad_f2ein(coin, cur, True)
    ad_buy_ein = await mcl.ad_f2ein(coin, cur, False)
    sad = await tcl.ad_new(ad_sell_ein)
    bad = await mcl.ad_new(ad_buy_ein)
    await tcl.ad_switch(sad.id, True)
    await mcl.ad_switch(bad.id, True)
    sad_in = await tcl.ad_epyd2pydin(sad)
    sad_db = await Ad.create(**sad_in.model_dump(exclude_none=True))
    bad_in = await mcl.ad_epyd2pydin(bad)
    await Ad.create(**bad_in.model_dump(exclude_none=True))

    order_epin: OrderEpydIn = await tcl.order_ad2epydin(sad_db, float(sad.orderAmountLimits.min))
    new_order: OrderEpyd = await tcl.order_request(order_epin)
    order_pin: OrderPydIn = await tcl.order_epyd2pydin(new_order)
    _order_db = await tcl.order_pydin2db(order_pin)

    # order_epin: OrderEpydIn = await tcl.order_ad2epydin(ad_db, float(mad.orderAmountLimits.min), cred_ids[0])
    # new_order: OrderEpyd = await tcl.order_request(order_epin)
    # order_pin: OrderPydIn = await tcl.order_epyd2pydin(new_order)
    # _order_db = await tcl.order_pydin2db(order_pin)

    await tcl.close(), await mcl.close()


if __name__ == "__main__":
    run(main())
