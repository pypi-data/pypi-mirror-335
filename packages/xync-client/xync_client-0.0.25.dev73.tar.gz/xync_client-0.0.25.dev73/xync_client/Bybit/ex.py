import json
from enum import IntEnum
from xync_schema.models import Cur

from xync_client.Abc.Base import ListOfDicts, MapOfIdsList, DictOfDicts, FlatDict
from xync_client.Abc.Ex import BaseExClient
from xync_client.pm_unifier import PmUnifier


class AdsStatus(IntEnum):
    REST = 0
    WORKING = 1


class ExClient(BaseExClient):  # Bybit client
    class BybitUnifier(PmUnifier):
        pm_map = {
            "Local Bank (R-Green)": "Sberbank",
            "Local Bank (S-Green)": "Sberbank",
            "Local Card (Red)": "Alfa-Bank",
            "Local Card (Yellow)": "T-Bank",
            "Local Card M-redTS": "MTS-bank",
            "Local Card-Green": "Sberbank",
            "Local Card-Yellow": "T-Bank",
        }

    host = "api2.bybit.com"
    headers = {"cookie": ";"}  # rewrite token for public methods
    unifier_class = BybitUnifier

    async def _get_config(self):
        resp = await self._get("/fiat/p2p/config/initial")
        return resp["result"]  # todo: tokens, pairs, ...

    # 19: Список поддерживаемых валют тейкера
    async def curs(self) -> FlatDict:
        config = await self._get_config()
        return {c["currencyId"]: c["currencyId"] for c in config["currencies"]}

    # 20: Список платежных методов
    async def pms(self, _: Cur = None) -> DictOfDicts:
        pms = await self._post("/fiat/otc/configuration/queryAllPaymentList/")
        pms = pms["result"]["paymentConfigVo"]
        return {
            pm["paymentType"]: {
                "name": pm["paymentName"],
            }
            for pm in pms
        }

    # 21: Список платежных методов по каждой валюте
    async def cur_pms_map(self) -> MapOfIdsList:
        pms = await self._post("/fiat/otc/configuration/queryAllPaymentList/")
        return json.loads(pms["result"]["currencyPaymentIdMap"])

    # 22: Список торгуемых монет (с ограничениям по валютам, если есть)
    async def coins(self) -> FlatDict:
        config = await self._get_config()
        cc: set[str] = set()
        for c in config["symbols"]:
            cc.add(c["tokenId"])
        return {c: c for c in cc}

    # 23: Список пар валюта/монет
    async def pairs(self) -> MapOfIdsList:
        config = await self._get_config()
        cc: dict[str, set[str]] = {}
        for c in config["symbols"]:
            cc[c["currencyId"]] = cc.get(c["currencyId"], set()) | {c["tokenId"]}
        return cc

    # 24: Список объяв по (buy/sell, cur, coin, pm)
    async def ads(
        self, coin_exid: str, cur_exid: str, is_sell: bool, pm_exids: list[str | int] = None, amount: int = None
    ) -> ListOfDicts:
        data = {
            "userId": "",
            "tokenId": coin_exid,
            "currencyId": cur_exid,
            "payment": pm_exids or [],
            "side": "0" if is_sell else "1",
            "size": "10",
            "page": "1",
            "amount": str(amount) if amount else "",
            "authMaker": False,
            "canTrade": False,
        }
        ads = await self._post("/fiat/otc/item/online/", data)
        return ads["result"]["items"]
