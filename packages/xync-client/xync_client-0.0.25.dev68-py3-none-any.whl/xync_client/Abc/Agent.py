from abc import abstractmethod

from pydantic import BaseModel
from tortoise.exceptions import IntegrityError
from x_model import HTTPException, FailReason
from xync_schema.models import OrderStatus, Coin, Cur, Ad, AdStatus, Fiat, Agent, Pmex, Pmcur, Cred, PmexBank
from xync_schema.pydantic import FiatNew, FiatUpd, BaseAd, FiatPydIn, AdSalePydIn, AdBuyPydIn, CredPydIn, BaseOrder

from xync_client.Abc.Ex import BaseExClient
from xync_client.Abc.Base import BaseClient


class BaseAgentClient(BaseClient):
    def __init__(self, agent: Agent):
        self.agent: Agent = agent
        super().__init__(self.agent.actor.ex)  # , "host_p2p"
        self.ex_client: BaseExClient = self.ex.client()

    @abstractmethod
    async def start_listen(self) -> bool: ...

    # 0: Получшение ордеров в статусе status, по монете coin, в валюте coin, в направлении is_sell: bool
    @abstractmethod
    async def get_orders(
        self, status: OrderStatus = OrderStatus.created, coin: Coin = None, cur: Cur = None, is_sell: bool = None
    ) -> list: ...

    # 3N: [T] - Уведомление об одобрении запроса на сделку
    @abstractmethod
    async def request_accepted_notify(self) -> int: ...  # id

    # 1: [T] Запрос на старт сделки
    @abstractmethod
    async def order_request(self, order: BaseOrder) -> dict: ...

    # async def start_order(self, order: Order) -> OrderOutClient:
    #     return OrderOutClient(self, order)

    # 1N: [M] - Запрос мейкеру на сделку
    @abstractmethod
    async def order_request_ask(self) -> dict: ...  # , ad: Ad, amount: float, pm: Pm, taker: Agent

    # 2N: [M] - Уведомление об отмене запроса на сделку
    @abstractmethod
    async def request_canceled_notify(self) -> int: ...  # id

    # # # Fiat
    async def _fiat_fpyd2pydin(
        self, fiat: FiatNew | FiatUpd
    ) -> tuple[int | str, str, str, str, str]:  # exid,cur,dtl,name,typ
        if not (pmex := await Pmex.get_or_none(ex=self.ex_client.ex, pm_id=fiat.pm_id).prefetch_related("pm")):
            # if no such pm on this ex - update ex.pms
            _res = await self.ex_client.set_pmcurexs()
            # and then get this pm again
            pmex = await Pmex.get(ex=self.ex_client.ex, pm_id=fiat.pm_id).prefetch_related("pm")
        cur = await Cur[fiat.cur_id]
        return pmex.exid, cur.ticker, fiat.detail, fiat.name or pmex.name, self.ex_client.pm_type_map(pmex)

    async def fiat_new_pyd2args(
        self, fiat: FiatNew
    ) -> tuple[int | str, str, str, str, str, None]:  # exid,cur,dtl,name,typ
        return await self._fiat_fpyd2pydin(fiat) + (None,)

    async def fiat_upd_pyd2args(
        self, fiat: FiatNew, fid: int
    ) -> tuple[int | str, str, str, str, str, int]:  # *new_p2args,id
        return await self._fiat_fpyd2pydin(fiat) + (fid,)

    @property
    @abstractmethod
    def fiat_pyd(self) -> BaseModel.__class__: ...

    @abstractmethod
    def fiat_args2pyd(
        self, exid: int | str, cur: str, detail: str, name: str, fid: int, typ: str, extra=None
    ) -> fiat_pyd: ...

    # 25: Список реквизитов моих платежных методов
    @abstractmethod
    async def creds(self) -> list: ...  # {fiat.exid: {fiat}}

    @staticmethod
    async def fiat_pyd2db(fiat_pyd: FiatNew | FiatUpd, uid: int, fid: int = None) -> tuple[Fiat, bool]:
        if not (pmcur := await Pmcur.get_or_none(cur_id=fiat_pyd.cur_id, pm_id=fiat_pyd.pm_id)):
            raise HTTPException(FailReason.body, f"No Pmcur with cur#{fiat_pyd.cur_id} and pm#{fiat_pyd.pm_id}", 404)
        df = {"detail": fiat_pyd.detail, "name": fiat_pyd.name, "amount": fiat_pyd.amount, "target": fiat_pyd.target}
        unq = {"pmcur": pmcur, "user_id": uid}
        if fid:
            unq["id"] = fid
        try:
            return await Fiat.update_or_create(df, **unq)
        except IntegrityError as e:
            raise HTTPException(FailReason.body, e)

    # 26: Создание реквизита моего платежного метода
    @abstractmethod
    async def fiat_f2in(self, fiat_new: FiatNew) -> FiatPydIn:
        if not (_pmcur := await Pmcur.get_or_none(cur_id=fiat_new.cur_id, pm_id=fiat_new.pm_id)):
            raise HTTPException(FailReason.body, f"No Pmcur with cur#{fiat_new.cur_id} and pm#{fiat_new.pm_id}", 404)
        # cred = await Cred.create({"exid": }, pmcur=pmcur, actor=self.agent.actor)
        # df = {"detail": fiat_pyd.detail, "name": fiat_pyd.name, "amount": fiat_pyd.amount, "target": fiat_pyd.target}
        # unq = {"pmcur": pmcur, "user_id": uid}

    # async def fiat_new(self, fiat: FiatNew) -> Fiat:
    #     actor = await Actor.get_or_create({"name": }, ex=self.ex_client.ex, exid=self.agent.actor.exid)
    #     FiatPydIn()
    #     fiat_db: Fiat = (await self.fiat_pyd2db(fiat, self.agent.user_id))[0]
    #     if not (fiatex := Fiatex.get_or_none(fiat=fiat_db, ex=self.agent.ex)):
    #         fiatex, _ = Fiatex.update_or_create({}, fiat=fiat_db, ex=self.agent.ex)
    #     return fiatex
    #
    # async def fiat_new(self, fiat: FiatNew) -> Fiat:
    #     FiatPydIn()
    #     fiat_db: Fiat = (await self.fiat_pyd2db(fiat, self.agent.user_id))[0]
    #     if not (fiatex := Fiatex.get_or_none(fiat=fiat_db, ex=self.agent.ex)):
    #         fiatex, _ = Fiatex.update_or_create({}, fiat=fiat_db, ex=self.agent.ex)
    #     return fiatex

    # 27: Редактирование реквизита моего платежного метода
    @abstractmethod
    async def fiat_upd(self, fiat_id: int, detail: str, name: str = None) -> Fiat: ...

    # 28: Удаление реквизита моего платежного метода
    @abstractmethod
    async def fiat_del(self, fiat_id: int) -> bool: ...

    # # # Ad
    # 29: Список моих объявлений
    @abstractmethod
    async def my_ads(self, status: AdStatus = None) -> list[BaseAd]: ...

    # 30: Создание объявления
    @abstractmethod
    async def ad_new(self, ad: BaseAd) -> Ad: ...

    # 31: Редактирование объявления
    @abstractmethod
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
    ) -> Ad: ...

    # 32: Удаление
    @abstractmethod
    async def ad_del(self, ad_id: int) -> bool: ...

    # 33: Вкл/выкл объявления
    @abstractmethod
    async def ad_switch(self, offer_id: int, active: bool) -> bool: ...

    # 34: Вкл/выкл всех объявлений
    @abstractmethod
    async def ads_switch(self, active: bool) -> bool: ...

    # # # User
    # 35: Получить объект юзера по его ид
    @abstractmethod
    async def get_user(self, user_id) -> dict: ...

    # 36: Отправка сообщения юзеру с приложенным файлом
    @abstractmethod
    async def send_user_msg(self, msg: str, file=None) -> bool: ...

    # 37: (Раз)Блокировать юзера
    @abstractmethod
    async def block_user(self, is_blocked: bool = True) -> bool: ...

    # 38: Поставить отзыв юзеру
    @abstractmethod
    async def rate_user(self, positive: bool) -> bool: ...

    # 39: Балансы моих монет
    @abstractmethod
    async def my_assets(self) -> dict: ...

    # Сохранение объявления (с Pm/Cred-ами) в бд
    async def ad_pydin2db(self, ad_pydin: AdSalePydIn | AdBuyPydIn) -> Ad:
        ad_db = await self.ex_client.ad_pydin2db(ad_pydin)
        await ad_db.creds.add(*getattr(ad_pydin, "creds_", []))
        return ad_db

    @staticmethod
    async def cred_pydin2db(cred: CredPydIn) -> Cred:
        df, unq = cred.args()
        cred_db, _ = await Cred.update_or_create(df, **unq)
        if cred.banks:
            await cred_db.banks.add(*[await PmexBank.get(exid=b) for b in cred.banks])
        return cred_db

    @staticmethod
    async def fiat_cred2db(cred: Cred) -> Fiat:
        fiat, _ = await Fiat.get_or_create(cred=cred)
        return fiat
