from x_client.http import Client as HttpClient
from xync_schema.models import Agent

from xync_client.Abc.AuthTrait import BaseAuthTrait
from xync_client.Abc.Base import BaseClient
from xync_client.TgWallet.pyro import PyroClient


class AuthClient(BaseAuthTrait, BaseClient):
    async def _get_auth_hdrs(self) -> dict[str, str]:
        if not self.agent:
            self.agent = (
                await Agent.filter(actor__ex=self.ex, auth__isnull=False)
                .prefetch_related("actor__person__user")
                .first()
            )
        pyro = PyroClient(self.agent)
        init_data = await pyro.get_init_data()
        tokens = HttpClient("walletbot.me")._post("/api/v1/users/auth/", init_data)
        self.agent.actor.exid = tokens["user_id"]
        await self.agent.actor.save()
        pref = "" if self.__class__.__name__ == "AssetClient" else "Bearer "
        return {"Wallet-Authorization": tokens["jwt"], "Authorization": pref + tokens["value"]}
