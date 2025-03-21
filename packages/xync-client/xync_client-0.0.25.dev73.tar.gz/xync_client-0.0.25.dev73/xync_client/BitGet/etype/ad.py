from typing import List, Optional
from pydantic import BaseModel, Field
from xync_schema.types import BaseAd


class PaymethodDetail(BaseModel):
    name: str
    required: int
    type: str


class PaymethodInfo(BaseModel):
    colorValue: str
    iconUrl: str
    isModifyKyc: int
    paymethodId: str
    paymethodInfo: List[PaymethodDetail]
    paymethodName: str
    paymethodNameHandle: bool


class Ad(BaseAd):
    exid: int | str | None = Field(alias="id")
    adEditorTime: str
    adNo: str
    adType: int
    advImages: List[str]
    advertiseIsEvent: int
    allowMerchantPlace: int
    allowPlace: int
    amount: str
    avgTime: int
    businessCertifiedList: List
    businessCertifiedResp: Optional[None]
    cancellPlaceOrderTime: int
    certifiedMerchant: int
    coinCode: str
    coinPrecision: int
    countryList: List
    createTime: str
    customizeState: int
    delAdv: int
    editAmount: str
    encryptUserId: str
    fiatCode: str
    fiatPrecision: int
    fiatSymbol: str
    floatValue: str
    fundState: bool
    goodEvaluationRate: str
    headColor: str
    hideFlag: int
    iconUrl: str
    lastAmount: str
    limitPrice: str
    maxAmount: str
    maxCompleteDefault: int
    minAmount: str
    minCompleteDefault: int
    nickName: str
    orderMode: str
    payDuration: int
    paymethodInfo: List[PaymethodInfo]
    positionNum: str
    price: str
    priceType: int
    priceValue: float
    recentOnlineText: str
    showOnline: bool
    soldAmount: str
    state: int
    taxAmount: str
    thirtyCompletionRate: str
    thirtyTunoverNum: str
    transactionTermsRespList: List
    turnoverNum: str
    turnoverRate: str
    turnoverRateNum: float  # Changed from int to float
    userId: str
