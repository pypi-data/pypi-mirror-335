from datetime import datetime
from enum import IntEnum
from typing import Union

from pydantic import BaseModel, Field, field_validator, model_validator

from dmtapi.constant import TZ_UTC


class PositionType(IntEnum):
    POSITION_TYPE_BUY = 0
    POSITION_TYPE_SELL = 1


class PositionReason(IntEnum):
    POSITION_REASON_CLIENT = 0
    POSITION_REASON_MOBILE = 1
    POSITION_REASON_WEB = 2
    POSITION_REASON_EXPERT = 3


class Position(BaseModel):
    """Model for open positions"""

    ticket: int
    time_msc: int
    time_update_msc: int
    date: Union[datetime, int] = Field(default=None, alias="time")
    date_update: Union[datetime, int] = Field(default=None, alias="time_update")
    type: PositionType
    magic: int = Field(default=0)
    identifier: int
    reason: PositionReason
    volume: float
    price_open: float
    sl: float = Field(default=0.0)
    tp: float = Field(default=0.0)
    price_current: float
    swap: float
    profit: float
    symbol: str
    comment: str = Field(default="")
    external_id: str = Field(default="")

    @field_validator("date", "date_update", mode="before")
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
    def coerce_model(cls, values):
        type_value = values.get("type")
        if isinstance(type_value, str):
            try:
                values["type"] = PositionType[type_value]
            except KeyError:
                raise ValueError(f"Invalid type value: {type_value}")
        elif isinstance(type_value, int):
            values["type"] = PositionType(type_value)

        reason_value = values.get("reason")
        if isinstance(reason_value, str):
            try:
                values["reason"] = PositionReason[reason_value]
            except KeyError:
                raise ValueError(f"Invalid reason value: {reason_value}")
        elif isinstance(reason_value, int):
            values["reason"] = PositionReason(reason_value)

        return values
