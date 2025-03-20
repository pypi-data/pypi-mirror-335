from asyncio import run
from urllib.parse import parse_qs
from pyrogram import Client
from pyrogram.raw import functions
from x_model import init_db
from xync_client.loader import TG_API_ID, TG_API_HASH, PG_DSN
from xync_schema import models
from xync_schema.models import Agent


class PyroClient:
    def __init__(self, agent: Agent):
        self.app: Client = Client(
            str(agent.actor.person.user.id), TG_API_ID, TG_API_HASH, session_string=agent.auth["sess"]
        )

    async def get_init_data(self) -> dict:
        async with self.app as app:
            app: Client
            bot = await app.resolve_peer("wallet")
            me = await app.resolve_peer(int(app.name))
            res = await app.invoke(functions.messages.RequestWebView(peer=me, bot=bot, platform="ios"))
            raw = parse_qs(res.url)["tgWebAppUserId"][0].split("#tgWebAppData=")[1]
            j = parse_qs(raw)
            return {
                "web_view_init_data": {
                    "query_id": j["query_id"][0],
                    "user": j["user"][0],
                    "auth_date": j["auth_date"][0],
                    "hash": j["hash"][0],
                },
                "web_view_init_data_raw": raw,
                "ep": "menu",
            }

    async def create_orders_forum(self, uid) -> int:
        async with self.app as app:
            app: Client
            forum = await app.create_supergroup(f"xync{uid}", "Xync Orders Group")
            await forum.add_members([uid, "xync_bot", "XyncNetBot"])
            return forum.id


async def main():
    _ = await init_db(PG_DSN, models, True)
    agent: Agent = await Agent.filter(auth__isnull=False, ex__name="TgWallet").prefetch_related("ex").first()
    pcl = PyroClient(agent)
    await pcl.create_orders_forum(agent.actor.user_id)


if __name__ == "__main__":
    run(main())
