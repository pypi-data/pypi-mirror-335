from pydantic import BaseModel
from x_model.types import New
from xync_schema.enums import PmType
from xync_schema.models import Country, Pm, Ex
from xync_schema.types import PmexBank

from xync_client.pm_unifier import PmUni


class PmTrait:
    typ: PmType | None = None
    logo: str | None = None
    banks: list[PmexBank] | None = None


class PmEx(BaseModel, PmTrait):
    exid: int | str
    name: str


class PmIn(New, PmUni, PmTrait):
    _unq = "norm", "country"
    country: Country | None = None

    class Config:
        arbitrary_types_allowed = True


class PmExIn(BaseModel):
    pm: Pm
    ex: Ex
    exid: int | str
    name: str

    class Config:
        arbitrary_types_allowed = True
