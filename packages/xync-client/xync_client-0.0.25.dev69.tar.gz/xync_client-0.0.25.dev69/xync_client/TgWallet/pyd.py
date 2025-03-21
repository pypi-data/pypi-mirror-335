from typing import Literal
from pydantic import BaseModel, computed_field
from xync_schema.types import BaseAd, BaseOrder


# Модели для вложенных структур
class UserStatistics(BaseModel):
    userId: int
    totalOrdersCount: int
    successRate: str
    successPercent: int


class User(BaseModel):
    userId: int
    nickname: str
    avatarCode: str
    statistics: UserStatistics
    isVerified: bool
    onlineStatus: str
    lastOnlineMinutesAgo: int | None = None


class AvailableVolume(BaseModel):
    currencyCode: str  # coin
    amount: str  # of asset


class Price(BaseModel):
    type: Literal["FLOATING", "FIXED"]
    baseCurrencyCode: str
    quoteCurrencyCode: str
    value: str
    estimated: str | None = None


class OrderLimitsIn(BaseModel):
    min: str  # In


class OrderLimits(OrderLimitsIn):
    currencyCode: str
    max: str
    approximate: bool


Status = Literal["ACTIVE", "INACTIVE", "ACTIVATING", "DEACTIVATING", "UPDATING"]


class ChangeLogItem(BaseModel):
    status: Status
    createDateTime: str
    initiatorUserId: int | None = None


class ChangeLog(BaseModel):
    items: list[ChangeLogItem]


class TakerFilter(BaseModel):
    accountAge: str
    completedOrders: str
    userRating: str


class Fee(BaseModel):
    rate: str
    availableVolume: AvailableVolume  # of asset


class KeyVal(BaseModel):
    value: str
    name: Literal["PAYMENT_DETAILS_NUMBER", "PHONE"] = "PAYMENT_DETAILS_NUMBER"


class BanksIn(BaseModel):
    value: list[str]
    name: Literal["BANKS"] = "BANKS"


class Bank(BaseModel):
    code: str
    nameRu: str
    nameEn: str


class Banks(BanksIn):
    value: list[Bank]


class Attrs(BaseModel):
    values: list[KeyVal]
    version: Literal["V1"] = "V1"


class AttrsV2In(BaseModel):
    version: Literal["V2"]
    values: list[KeyVal | BanksIn]


class AttrsV2(AttrsV2In):
    values: list[KeyVal | Banks]


class PmEpyd(BaseModel):
    code: str
    name: str
    originNameLocale: str
    nameEng: str


class PmEpydRoot(PmEpyd):
    banks: list[PmEpyd] | None = None


class FiatEpydIn(BaseModel):
    paymentMethodCode: str
    currencyCode: str
    name: str
    attributes: Attrs | AttrsV2In


class CredEpyd(BaseModel):
    id: int
    userId: int
    paymentMethod: PmEpydRoot
    currency: str
    attributes: Attrs | AttrsV2
    name: str = ""


class InitVolume(BaseModel):
    currencyCode: str  # coin
    amount: str  # of asset


AdType = Literal["PURCHASE", "SALE"]


# Основные модели
class _BaseInOutAd(BaseAd):
    type: AdType
    price: Price


class _BaseAd(_BaseInOutAd):
    number: str
    orderAmountLimits: OrderLimits  # fiat
    orderVolumeLimits: OrderLimits  # asset
    availableVolume: AvailableVolume

    @computed_field
    @property
    def is_sell(self) -> bool:
        return self.type == "SALE"


class _PmsTrait:
    paymentMethods: list[PmEpydRoot]


class _StatusTrait:
    status: str  # maker | One


class _UserTrait:
    takerFilter: TakerFilter  # taker | One
    user: User  # taker | One


PaymentConfirmTimeout = Literal["PT3M", "PT15M", "PT30M", "PT45M", "PT1H", "PT2H", "PT3H"]


class _OneTrait(_StatusTrait, _UserTrait):
    comment: str
    changeLog: ChangeLog
    createDateTime: str
    paymentConfirmTimeout: PaymentConfirmTimeout


class _TakerOne(_BaseAd, _OneTrait):
    orderConfirmationTimeout: Literal["PT1M30S", "PT3M", "PT15M"]
    orderAcceptTimeout: Literal["PT10M"]


class AdTakerSaleBuy(_BaseAd, _PmsTrait, _UserTrait):
    availableVolume: str


class OneAdTakerMakerSale(_TakerOne):
    paymentDetails: list[CredEpyd]
    fee: Fee


class OneAdTakerBuy(_TakerOne, _PmsTrait): ...


class AdMakerBuy(_BaseAd, _PmsTrait, _StatusTrait): ...


class OneAdMakerBuy(_BaseAd, _OneTrait, _PmsTrait): ...


class AdMakerSale(_BaseAd, _StatusTrait):
    paymentDetails: list[CredEpyd]


# # #


# In
class _BaseIn(_BaseInOutAd):
    orderRoundingRequired: bool
    orderAmountLimits: OrderLimitsIn
    paymentConfirmTimeout: PaymentConfirmTimeout
    comment: str
    takerFilter: TakerFilter | None = None


class _AdNew(_BaseIn):
    initVolume: AvailableVolume


class _AdUpd(_BaseIn):
    offerId: int
    volume: str  # int


class _SaleInTrait:
    paymentDetailsIds: list[int]


class _BuyInTrait:
    paymentMethodCodes: list[str]


class AdMakerNewSale(_AdNew, _SaleInTrait): ...


class AdMakerUpdSale(_AdUpd, _SaleInTrait): ...


class AdMakerNewBuy(_AdNew, _BuyInTrait): ...


class AdMakerUpdBuy(_AdUpd, _BuyInTrait): ...


OrderStatus = Literal["ACTIVE", "DRAFT"]


class OrderEpydIn(BaseOrder):
    offerId: int
    type: AdType
    paymentDetailsId: int
    amount: AvailableVolume


class OrderEpyd(BaseModel):
    id: int
    number: str
    seller: User
    buyer: User
    offerId: int
    offerType: AdType
    isExpress: bool
    price: Price
    paymentDetails: CredEpyd
    volume: AvailableVolume
    amount: AvailableVolume
    feeVolume: AvailableVolume
    paymentConfirmTimeout: PaymentConfirmTimeout
    buyerSendingPaymentConfirmationTimeout: Literal["PT15M"]
    createDateTime: str
    statusUpdateDateTime: str
    holdRestrictionsWillBeApplied: bool
    status: OrderStatus
    changeLog: ChangeLog
    isAutoAccept: bool
    offerComment: str = ""

    @computed_field
    @property
    def is_sell(self) -> bool:
        return self.offerType == "SALE"
