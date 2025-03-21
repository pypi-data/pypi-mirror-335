import json
import subprocess
from asyncio import run, sleep
from os.path import dirname

from x_model import init_db
from xync_schema import models
from xync_schema.models import Ex
from xync_schema import types

from xync_client.Abc.Ex import BaseExClient
from xync_client.loader import PG_DSN
from xync_client.Abc.Base import MapOfIdsList
from xync_client.Abc.types import PmEx
from xync_client.BitGet.etype import ad


class ExClient(BaseExClient):
    headers = {
        "accept-language": "ru,en;q=0.9",
        "content-type": "application/json;charset=UTF-8",
        "deviceid": "883e1394d8a2278418b6f02804df16c4",
    }

    async def _coin_cur_pms(self) -> dict:
        # curs = (await self._post("/v1/p2p/pub/currency/queryAllCoinAndFiat"))["data"]["fiatInfoRespList"]
        p = subprocess.Popen(
            [
                "node",
                dirname(__file__) + "/req.mjs",
                "pub/currency/queryAllCoinAndFiat",
                "{}",
                json.dumps(self.headers, separators=(",", ":")),
            ],
            stdout=subprocess.PIPE,
        )
        out = p.stdout.read().decode()
        if not out:
            await sleep(1.6)
            return await self.curs()
        return json.loads(out)

    async def curs(self) -> dict[str, types.CurEx]:
        curs: list[dict] = (await self._coin_cur_pms())["fiatInfoRespList"]
        return {cur["fiatCode"]: types.CurEx(exid=cur["fiatCode"], ticker=cur["fiatCode"]) for cur in curs}

    async def coins(self) -> dict[str, types.CoinEx]:
        coins: list[dict] = (await self._coin_cur_pms())["coinInfoRespList"]
        return {
            coin["coinCode"]: types.CoinEx(exid=coin["coinCode"], ticker=coin["coinCode"], scale=coin["coinPrecision"])
            for coin in coins
        }

    async def pairs(self) -> MapOfIdsList:
        coins = (await self.coins()).keys()
        curs = (await self.curs()).keys()
        p = {cur: {c for c in coins} for cur in curs}
        return p, p

    async def pms(self, cur: str = None) -> dict[int | str, PmEx]:  # {pm.exid: pm}
        pp = {}
        pms: list[dict] = (await self._coin_cur_pms())["fiatInfoRespList"]
        for pm in pms:
            for p in pm["paymethodInfo"]:
                pp[p["paymethodId"]] = PmEx(exid=p["paymethodId"], name=p["paymethodName"])
        return pp

    async def ads(
        self, coin_exid: str, cur_exid: str, is_sell: bool, pm_exids: list[str | int] = None, amount: int = None
    ) -> list[ad.Ad]:
        request_data = {
            "side": 1 if is_sell else 2,
            "pageNo": 1,
            "pageSize": 10,
            "coinCode": coin_exid,
            "fiatCode": cur_exid,
            "paymethodId": pm_exids or "",
            "languageType": 6,
        }
        request_json = json.dumps(request_data, separators=(",", ":"))
        p = subprocess.Popen(
            [
                "node",
                dirname(__file__) + "/req.mjs",
                "pub/adv/queryAdvList",
                request_json,
                json.dumps(self.headers, separators=(",", ":")),
            ],
            stdout=subprocess.PIPE,
        )
        out = p.stdout.read().decode()
        ads = json.loads(out)
        return [ad.Ad(id=_ad["encryptUserId"], **_ad) for _ad in ads["dataList"]]

    async def cur_pms_map(self) -> dict[str, list[int]]:
        cur_pms_map: list[dict] = (await self._coin_cur_pms())["fiatInfoRespList"]
        return {item["fiatCode"]: [pms["paymethodId"] for pms in item["paymethodInfo"]] for item in cur_pms_map}


async def main():
    _ = await init_db(PG_DSN, models, True)
    bg = await Ex.get(name="BitGet")
    cl = ExClient(bg)
    await cl.curs()
    # await cl.coins()
    _ads = await cl.ads("BTC", "RUB", True, [1, 289, 375])
    # await cl.pms()
    await cl.cur_pms_map()
    await cl.set_pmcurexs()
    await cl.set_coinexs()
    await cl.close()


if __name__ == "__main__":
    run(main())
