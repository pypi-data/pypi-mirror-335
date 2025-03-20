from datetime import datetime
from enum import Enum
from typing import Union

from pydantic import BaseModel, Field, model_validator, field_validator

from dmtapi.constant import TZ_UTC


class PlaceOrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    BUYLIMIT = "BUYLIMIT"
    SELLLIMIT = "SELLLIMIT"
    BUYSTOP = "BUYSTOP"
    SELLSTOP = "SELLSTOP"


class OrderTypeEnum(Enum):
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1
    ORDER_TYPE_BUY_LIMIT = 2
    ORDER_TYPE_SELL_LIMIT = 3
    ORDER_TYPE_BUY_STOP = 4
    ORDER_TYPE_SELL_STOP = 5
    ORDER_TYPE_BUY_STOP_LIMIT = 6
    ORDER_TYPE_SELL_STOP_LIMIT = 7
    ORDER_TYPE_CLOSE_BY = 8


order_type_enum_map = {
    OrderTypeEnum.ORDER_TYPE_BUY: PlaceOrderType.BUY,
    OrderTypeEnum.ORDER_TYPE_SELL: PlaceOrderType.SELL,
    OrderTypeEnum.ORDER_TYPE_BUY_LIMIT: PlaceOrderType.BUYLIMIT,
    OrderTypeEnum.ORDER_TYPE_SELL_LIMIT: PlaceOrderType.SELLLIMIT,
    OrderTypeEnum.ORDER_TYPE_BUY_STOP: PlaceOrderType.BUYSTOP,
    OrderTypeEnum.ORDER_TYPE_SELL_STOP: PlaceOrderType.SELLSTOP,
}


class OrderStateEnum(Enum):
    ORDER_STATE_STARTED = 0
    ORDER_STATE_PLACED = 1
    ORDER_STATE_CANCELED = 2
    ORDER_STATE_PARTIAL = 3
    ORDER_STATE_FILLED = 4
    ORDER_STATE_REJECTED = 5
    ORDER_STATE_EXPIRED = 6
    ORDER_STATE_REQUEST_ADD = 7
    ORDER_STATE_REQUEST_MODIFY = 8
    ORDER_STATE_REQUEST_CANCEL = 9


class OrderReasonEnum(Enum):
    ORDER_REASON_CLIENT = 0
    ORDER_REASON_MOBILE = 1
    ORDER_REASON_WEB = 2
    ORDER_REASON_EXPERT = 3
    ORDER_REASON_SL = 4
    ORDER_REASON_TP = 5
    ORDER_REASON_SO = 6


class OrderTypeTimeEnum(Enum):
    ORDER_TIME_GTC = 0
    ORDER_TIME_DAY = 1
    ORDER_TIME_SPECIFIED = 2
    ORDER_TIME_SPECIFIED_DAY = 3


class TradeOrder(BaseModel):
    """Model for pending orders"""

    # https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties
    ticket: int
    time_setup: Union[datetime, int] = Field(default=None, alias="time_setup")
    time_setup_msc: int
    time_done: Union[datetime, int, None] = Field(default=None, alias="time_done")
    time_done_msc: int
    time_expiration: Union[int, None] = Field(default=None)
    type: OrderTypeEnum
    type_time: OrderTypeTimeEnum
    state: OrderStateEnum
    magic: int
    position_id: int
    position_by_id: int
    reason: OrderReasonEnum
    volume_initial: float
    volume_current: float
    price_open: float
    sl: float
    tp: float
    price_current: float
    price_stoplimit: float
    symbol: str
    comment: str
    external_id: str

    @field_validator("time_setup", "time_done", "time_expiration", mode="before")
    def validate_inception_date(cls, v):
        if isinstance(v, str):
            if v == "null":
                return None
            try:
                # 2024.09.11 16:29:16
                return datetime.strptime(v, "%Y.%m.%d %H:%M:%S").astimezone(tz=TZ_UTC)
            except ValueError:
                # 2024-08-10T07:38:46+00:00
                return datetime.fromisoformat(v).astimezone(tz=TZ_UTC)
        elif isinstance(v, int):
            if v == 0:
                return None
            return datetime.fromtimestamp(v / 1000).astimezone(tz=TZ_UTC)

        return v

    @model_validator(mode="before")
    def coerce_model(cls, values):
        state_value = values.get("state")
        if isinstance(state_value, str):
            try:
                values["state"] = OrderStateEnum[state_value]
            except KeyError:
                raise ValueError(f"Invalid entry value: {state_value}")
        elif isinstance(state_value, int):
            values["state"] = OrderStateEnum(state_value)

        reason_value = values.get("reason")
        if isinstance(reason_value, str):
            try:
                values["reason"] = OrderReasonEnum[reason_value]
            except KeyError:
                raise ValueError(f"Invalid reason value: {reason_value}")
        elif isinstance(reason_value, int):
            values["reason"] = OrderReasonEnum(reason_value)

        type_time_value = values.get("type_time")
        if isinstance(type_time_value, str):
            try:
                values["type_time"] = OrderTypeTimeEnum[type_time_value]
            except KeyError:
                raise ValueError(f"Invalid type_time value: {type_time_value}")
        elif isinstance(type_time_value, int):
            values["type_time"] = OrderTypeTimeEnum(type_time_value)

        type_value = values.get("type")
        if isinstance(type_value, str):
            try:
                values["type"] = OrderTypeEnum[type_value]
            except KeyError:
                raise ValueError(f"Invalid type value: {type_value}")
        elif isinstance(type_value, int):
            values["type"] = OrderTypeEnum(type_value)

        return values
