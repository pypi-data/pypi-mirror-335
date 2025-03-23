from datetime import datetime
from pydantic import BaseModel, Field
from x_model.types import New

from xync_schema.enums import AdStatus, OrderStatus
from xync_schema import models


class UnitEx(BaseModel):
    exid: int | str
    ticker: str
    scale: int = None
    rate: float | None = None


class CoinEx(UnitEx):
    p2p: bool = None
    minimum: float | None = None


class CurEx(UnitEx):
    rounding_scale: int | None = None
    minimum: int | None = None


class PmexBank(BaseModel):
    # id: int | None = None
    exid: str
    name: str


# class Pmcur(Struct):
#     id: int | None = None
#     pm_id: int
#     cur_id: int


class CredIn(New):
    exid: int
    pmcur: models.Pmcur
    actor: models.Actor
    detail: str = ""
    name: str = ""
    id: int | None = None
    banks: list[str] | None = None
    _unq = "id", "exid", "ch", "pmcur"

    class Config:
        arbitrary_types_allowed = True


class FiatIn(New):
    cred: models.Cred
    amount: float
    id: int = None
    target: float | None = None
    _unq = "id", "cred"

    class Config:
        arbitrary_types_allowed = True


class BaseAd(BaseModel):
    price: float
    exid: int | None = Field(alias="id")


class BaseAdIn(BaseAd, New):
    min_fiat: float
    max_fiat: float
    direction: models.Direction
    detail: str | None = None
    auto_msg: str | None = None
    status: AdStatus = AdStatus.active
    maker: models.Actor = None
    _unq = "exid", "maker", "direction"

    class Config:
        arbitrary_types_allowed = True


class AdBuyIn(BaseAdIn):
    pms_: list[models.Pm]


class AdSaleIn(BaseAdIn):
    creds_: list[models.Cred]


class BaseOrder(BaseModel):
    id: int | None = None


class Order(BaseModel):
    id: int
    amount: float
    status: str
    cred: models.Cred.out_type()
    is_sell: bool
    created_at: datetime
    topic: int
    actions: dict | None = {}
    actor: int | None = None
    payed_at: datetime | None = None
    appealed_at: datetime | None = None
    confirmed_at: datetime | None = None
    msgs: int = 0


class OrderIn(BaseModel):
    exid: int
    amount: float
    created_at: datetime
    ad: models.Ad
    cred: models.Cred
    taker: models.Actor
    id: int = None
    maker_topic: int | None = None
    taker_topic: int | None = None
    status: OrderStatus = OrderStatus.created
    payed_at: datetime | None = None
    confirmed_at: datetime | None = None
    appealed_at: datetime | None = None
    _unq = "id", "exid", "amount", "maker_topic", "taker_topic", "ad", "cred", "taker"

    class Config:
        arbitrary_types_allowed = True


class UreadMsgs(BaseModel):
    order_id: int
    unread_cnt: int
