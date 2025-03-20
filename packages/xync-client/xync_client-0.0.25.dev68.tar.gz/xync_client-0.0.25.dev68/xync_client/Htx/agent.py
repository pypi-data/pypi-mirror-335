from x_client.aiohttp import Client
from xync_schema.enums import AdStatus, PmType, OrderStatus
from xync_schema.models import Pm, Coin, Cur, Ad, Fiat, Order
from xync_schema.pydantic import FiatNew

from xync_client.Abc.Agent import BaseAgentClient

url_ads_req = "https://otc-cf.huobi.com/v1/data/trade-market"
url_ads_web = "https://www.huobi.com/en-us/fiat-crypto/trade/"
url_my_ads = "https://otc-api.trygofast.com/v1/data/trade-list?pageSize=50"
url_my_ad = "https://www.huobi.com/-/x/otc/v1/otc/trade/"  # + id
url_my_bals = "https://www.huobi.com/-/x/otc/v1/capital/balance"
url_paccs = "https://www.huobi.com/-/x/otc/v1/user/receipt-account"


class Public(Client):
    url_ads_web = "https://www.huobi.com/en-us/fiat-crypto/trade/"


class Private(BaseAgentClient):
    # 0
    async def get_orders(
        self, stauts: OrderStatus = OrderStatus.created, coin: Coin = None, cur: Cur = None, is_sell: bool = None
    ) -> list[Order]:
        pass

    async def order_request(self, ad_id: int, amount: float) -> dict:
        pass

    async def my_fiats(self, cur: Cur = None) -> list[dict]:
        pass

    async def fiat_new(self, fiat: FiatNew) -> Fiat.pyd():
        pass

    async def fiat_upd(self, detail: str = None, typ: PmType = None) -> bool:
        pass

    async def fiat_del(self, fiat_id: int) -> bool:
        pass

    async def my_ads(self) -> list[dict]:
        res = await self._get(url_my_ads)
        ads: [] = res["data"]
        if (pages := res["totalPage"]) > 1:
            for p in range(2, pages + 1):
                ads += (await self._get(url_my_ads, {"currPage": p})).get("data", False)
        return ads

    async def ad_new(
        self,
        coin: Coin,
        cur: Cur,
        is_sell: bool,
        pms: list[Pm],
        price: float,
        is_float: bool = True,
        min_fiat: int = None,
        details: str = None,
        autoreply: str = None,
        status: AdStatus = AdStatus.active,
    ) -> Ad:
        pass

    async def ad_upd(
        self,
        pms: [Pm] = None,
        price: float = None,
        is_float: bool = None,
        min_fiat: int = None,
        details: str = None,
        autoreply: str = None,
        status: AdStatus = None,
    ) -> bool:
        pass

    async def ad_del(self) -> bool:
        pass

    async def ad_switch(self) -> bool:
        pass

    async def ads_switch(self) -> bool:
        pass

    async def get_user(self, user_id: int) -> dict:
        user = (await self._get(f"/-/x/otc/v1/user/{user_id}/info"))["data"]
        return user

    async def send_user_msg(self, msg: str, file=None) -> bool:
        pass

    async def block_user(self, is_blocked: bool = True) -> bool:
        pass

    async def rate_user(self, positive: bool) -> bool:
        pass

    # 39
    async def my_assets(self) -> dict:
        assets = await self._get(url_my_bals)
        return {c["coinId"]: c["total"] for c in assets["data"] if c["total"]}

    async def _get_auth_hdrs(self) -> dict[str, str]:
        pass

    base_url = ""
    middle_url = ""

    htok: str = "Ev5lFfAvxDU2MA9BJ-Mc4U6zZG3Wb6qsp3Tx2fz6GIoY-uOP2m0-gvjE57ad1qDF"

    url_ads_req = "https://otc-cf.huobi.com/v1/data/trade-market"
    url_my_ads = "https://otc-api.trygofast.com/v1/data/trade-list?pageSize=50"
    url_my_ad = "https://www.huobi.com/-/x/otc/v1/otc/trade/"  # + id
    url_my_bals = "https://www.huobi.com/-/x/otc/v1/capital/balance"
    url_paccs = "https://www.huobi.com/-/x/otc/v1/user/receipt-account"
