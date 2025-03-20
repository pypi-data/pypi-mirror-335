from datetime import datetime
from enum import IntEnum

from pydantic import BaseModel, Field, field_validator, model_validator

from dmtapi.constant import TZ_UTC


class DealType(IntEnum):
    # https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties#enum_deal_type
    DEAL_TYPE_BUY = 0
    DEAL_TYPE_SELL = 1
    DEAL_TYPE_BALANCE = 2
    DEAL_TYPE_CREDIT = 3
    DEAL_TYPE_CHARGE = 4
    DEAL_TYPE_CORRECTION = 5
    DEAL_TYPE_BONUS = 6
    DEAL_TYPE_COMMISSION = 7
    DEAL_TYPE_COMMISSION_DAILY = 8
    DEAL_TYPE_COMMISSION_MONTHLY = 9
    DEAL_TYPE_COMMISSION_AGENT_DAILY = 10
    DEAL_TYPE_COMMISSION_AGENT_MONTHLY = 11
    DEAL_TYPE_INTEREST = 12
    DEAL_TYPE_BUY_CANCELED = 13
    DEAL_TYPE_SELL_CANCELED = 14
    DEAL_DIVIDEND = 15
    DEAL_DIVIDEND_FRANKED = 16
    DEAL_TAX = 17


class DealTypeEntry(IntEnum):
    DEAL_ENTRY_IN = 0
    DEAL_ENTRY_OUT = 1
    DEAL_ENTRY_INOUT = 2
    DEAL_ENTRY_OUT_BY = 3


class DealReason(IntEnum):
    DEAL_REASON_CLIENT = 0
    DEAL_REASON_MOBILE = 1
    DEAL_REASON_WEB = 2
    DEAL_REASON_EXPERT = 3
    DEAL_REASON_SL = 4
    DEAL_REASON_TP = 5
    DEAL_REASON_SO = 6
    DEAL_REASON_ROLLOVER = 7
    DEAL_REASON_VMARGIN = 8
    DEAL_REASON_SPLIT = 9
    DEAL_REASON_CORPORATE_ACTION = 10


class TradeDeal(BaseModel):
    # https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties#enum_deal_type
    ticket: int
    order: int = Field(default=0)
    time: datetime = Field(default=None)
    time_msc: int
    type: DealType
    entry: DealTypeEntry
    magic: int = Field(default=0)
    position_id: int = Field(default=0)
    reason: DealReason = Field(default=0)
    volume: float = Field(default=0.0)
    price: float = Field(default=0.0)
    commission: float = Field(default=0.0)
    swap: float = Field(default=0.0)
    profit: float
    fee: float = Field(default=0.0)
    symbol: str = Field(default="")
    comment: str = Field(default="")
    external_id: str = Field(default="")

    @field_validator("time", mode="before")
    def validate_inception_date(cls, v):
        if isinstance(v, str):
            try:
                # 2024.09.11 16:29:16
                return datetime.strptime(v, "%Y.%m.%d %H:%M:%S").astimezone(tz=TZ_UTC)
            except ValueError:
                # 2024-08-10T07:38:46+00:00
                return datetime.fromisoformat(v).astimezone(tz=TZ_UTC)
        elif isinstance(v, int):
            return datetime.fromtimestamp(v / 1000).astimezone(tz=TZ_UTC)

        return v

    @model_validator(mode="before")
    def coerce_entry(cls, values):
        entry_value = values.get("entry")
        if isinstance(entry_value, str):
            try:
                values["entry"] = DealTypeEntry[entry_value]
            except KeyError:
                raise ValueError(f"Invalid entry value: {entry_value}")
        elif isinstance(entry_value, int):
            values["entry"] = DealTypeEntry(entry_value)

        reason_value = values.get("reason")
        if isinstance(reason_value, str):
            try:
                values["reason"] = DealReason[reason_value]
            except KeyError:
                raise ValueError(f"Invalid reason value: {reason_value}")
        elif isinstance(reason_value, int):
            values["reason"] = DealReason(reason_value)
        return values
