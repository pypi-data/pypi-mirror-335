import logging

import pytest
from xync_schema.enums import ExStatus, ExAction
from xync_schema.models import Ex, TestEx, Fiat, Ad, Coin, Cur
from xync_schema.types import FiatNew, BaseAd

from xync_client.Abc.Base import DictOfDicts, ListOfDicts
from xync_client.Abc.BaseTest import BaseTest
from xync_client.Abc.Ex import BaseExClient
from xync_client.Abc.Agent import BaseAgentClient

import TestEx as Tex


@pytest.mark.asyncio(loop_scope="session")
class TestAgent(BaseTest):
    @pytest.fixture(scope="class", autouse=True)
    async def clients(self) -> tuple[BaseAgentClient, BaseAgentClient]:
        exs = (
            await Ex.filter(status__gt=ExStatus.plan, agents__auth__isnull=False)
            .distinct()
            .prefetch_related("agents__ex")
        )
        agents = [[ag for ag in ex.agents if ag.auth][:2] for ex in exs]
        clients: list[tuple[BaseAgentClient, BaseAgentClient]] = [(t.client(), m.client()) for t, m in agents]
        yield clients
        [(await taker.close(), await maker.close()) for taker, maker in clients]

    # 42
    async def test_ad(self, clients: list[BaseExClient]):
        Tex(self)
        for client in clients:
            if not self.ad.get(client.ex.id):
                await self.test_ads(clients)
            ad: BaseAd = await client.ad(self.ad[client.ex.id].id)
            ok = isinstance(ad, BaseAd)
            t, _ = await TestEx.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.ad)
            assert t.ok, "No ad"
            logging.info(f"{client.ex.name}: {ExAction.ad.name} - ok")

    # 0
    async def test_get_orders(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            get_orders: ListOfDicts = await taker.get_orders()
            ok = self.is_list_of_dicts(get_orders, False)
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.get_orders)
            assert t.ok, "No get orders"
            logging.info(f"{taker.agent.ex_id}:{ExAction.get_orders.name} - ok")

    # 1
    async def test_order_request(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            await taker.agent.fetch_related("ex", "ex__agents")
            ex_client: BaseExClient = taker.agent.ex.client()
            ads = await ex_client.ads("USDT", "RUB", False)
            for ad in ads:
                order_request: dict | bool = await taker.order_request(ad["id"], ad["orderAmountLimits"]["min"])
                if order_request:
                    break
            ok = order_request["status"] == "SUCCESS"
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.order_request)
            assert t.ok, "No get orders"
            logging.info(f"{taker.agent.ex_id}:{ExAction.order_request.name} - ok")

    # 25
    async def test_my_fiats(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            my_fiats: DictOfDicts = await taker.my_fiats()
            ok = self.is_dict_of_dicts(my_fiats)
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.my_fiats)
            assert t.ok, "No my fiats"
            logging.info(f"{taker.agent.ex_id}:{ExAction.my_fiats.name} - ok")

    # 26
    async def test_fiat_new(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            fn = FiatNew(cur_id=11, pm_id=22, detail="123456789")
            fiat_new: Fiat = await taker.fiat_new(fn)
            ok = isinstance(fiat_new, Fiat)
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.fiat_new)
            assert t.ok, "No add fiat"
            logging.info(f"{taker.agent.ex_id}:{ExAction.fiat_new.name} - ok")

    # 27
    async def test_fiat_upd(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            my_fiats = await taker.my_fiats()
            fiats = [fiat for fiat in my_fiats.values()]
            fiat_upd: Fiat = await taker.fiat_upd(fiat_id=fiats[0]["id"], detail="347890789")
            ok = isinstance(fiat_upd, Fiat)
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.fiat_upd)
            assert t.ok, "No upd fiat"
            logging.info(f"{taker.agent.ex_id}:{ExAction.fiat_upd.name} - ok")

    # 28
    async def test_fiat_del(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            my_fiats = await taker.my_fiats()
            fiats = [fiat for fiat in my_fiats.values()]
            fiat_del: bool = await taker.fiat_del(fiat_id=fiats[0]["id"])
            ok = fiat_del["status"] == "SUCCESS"
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.fiat_del)
            assert t.ok, "No del fiat"
            logging.info(f"{taker.agent.ex_id}:{ExAction.fiat_del.name} - ok")

    # 29
    async def test_my_ads(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            my_ads: ListOfDicts = await taker.my_ads()
            ok = self.is_list_of_dicts(my_ads, False)
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.my_ads)
            assert t.ok, "No del fiat"
            logging.info(f"{taker.agent.ex_id}:{ExAction.my_ads.name} - ok")

    # 30
    async def test_ad_new(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            my_fiats = await taker.my_fiats()
            my_fiat = list(my_fiats.values())[0]
            coin = await Coin.get(ticker="USDT")
            cur = await Cur.get(ticker=my_fiat["currency"])
            # pm = await Fiatex.get()
            ad_new: Ad.pyd() = await taker.ad_new(
                coin=coin, cur=cur, is_sell=True, fiats=[my_fiat["id"]], amount="10", price="120", min_fiat="500"
            )
            ok = ad_new["status"] == "SUCCESS"
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.ad_new)
            assert t.ok, "No add new ad"
            logging.info(f"{taker.agent.ex_id}:{ExAction.ad_new.name} - ok")

    # 31
    async def test_ad_upd(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            my_ads: ListOfDicts = await taker.my_ads()
            ad_upd: Ad.pyd() = await taker.ad_upd(offer_id=my_ads[0]["id"], amount="11")
            ok = ad_upd["status"] == "SUCCESS"
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.ad_upd)
            assert t.ok, "No add new ad"
            logging.info(f"{taker.agent.ex_id}:{ExAction.ad_upd.name} - ok")

    # 32
    async def test_ad_del(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            my_ads: ListOfDicts = await taker.my_ads()
            ad_del: bool = await taker.ad_del(offer_id=my_ads[0]["id"])
            t, _ = await TestEx.update_or_create({"ok": ad_del}, ex_id=taker.agent.ex_id, action=ExAction.ad_del)
            assert t.ok, "No add new ad"
            logging.info(f"{taker.agent.ex_id}:{ExAction.ad_del.name} - ok")

    # 33
    async def test_ad_switch(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            my_ads: ListOfDicts = await taker.my_ads()
            new_status = not (my_ads[0]["status"] == "ACTIVE")
            ad_switch: bool = await taker.ad_switch(offer_id=my_ads[0]["id"], active=new_status)
            t, _ = await TestEx.update_or_create({"ok": ad_switch}, ex_id=taker.agent.ex_id, action=ExAction.ad_switch)
            assert t.ok, "No ad active/off"
            logging.info(f"{taker.agent.ex_id}:{ExAction.ad_switch.name} - ok")

    # 34
    async def test_ads_switch(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            ads_switch: bool = await taker.ads_switch(active=False)
            t, _ = await TestEx.update_or_create(
                {"ok": ads_switch}, ex_id=taker.agent.ex_id, action=ExAction.ads_switch
            )
            assert t.ok, "No ads switch"
            logging.info(f"{taker.agent.ex_id}:{ExAction.ads_switch.name} - ok")

    # 35
    async def test_get_user(self, clients: list[BaseAgentClient]):
        for taker, maker in clients:
            await taker.agent.fetch_related("ex", "ex__agents")
            ex_client: BaseExClient = taker.agent.ex.client()
            ads = await ex_client.ads("NOT", "RUB", False)
            user_info = await taker.get_user(offer_id=ads[0]["id"])
            ok = isinstance(user_info, dict) and user_info
            t, _ = await TestEx.update_or_create({"ok": ok}, ex_id=taker.agent.ex_id, action=ExAction.get_user)
            assert t.ok, "No get user information"
            logging.info(f"{taker.agent.ex_id}:{ExAction.get_user.name} - ok")
