from x_client.aiohttp import Client
from xync_schema.models import Ex

DictOfDicts = dict[int | str, dict]
ListOfDicts = list[dict]
FlatDict = dict[int | str, str]
MapOfIdsList = dict[int | str, list[int | str]]


class BaseClient(Client):
    ex: Ex

    def __init__(self, ex: Ex, attr: str = "host_p2p"):
        self.ex = ex
        super().__init__(getattr(ex, attr))
