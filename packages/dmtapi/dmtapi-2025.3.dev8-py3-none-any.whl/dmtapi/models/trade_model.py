from typing import Optional

from pydantic import BaseModel, Field, field_validator
from typing_extensions import TypedDict


class TakeProfit(TypedDict):
    """
    Take profit level configuration.
    If you have provided price then tp_as_pip and tp_as_pct are ignored.
    If you have not provided price then tp_as_pip or tp_as_pct is used, whichever is provided.
    This is good when you do not want to calculate the price and just want to set tp as pips or percentage.
    close_pct is the percentage of volume to close at this take profit level, min value is 0 and max is 1.
    close_pct=0.5 means close 50% of the volume at this take profit level.

    Attributes:
        price (float): Price level.
        close_pct (float): Close percentage.
        tp_as_pip (Optional[float]): Take profit in pips. Set to 0 if not used.
        tp_as_pct (Optional[float]): Take profit as percentage. Set to 0 if not used.
    """

    price: float
    close_pct: float
    tp_as_pip: Optional[float]
    tp_as_pct: Optional[float]


class TradeSetup(BaseModel):
    """
    Configuration for opening a new trade.

    Attributes:
        symbol (str): Trading symbol (e.g., "EURUSD").
        volume (float): Trading volume (0-100).
        direction (TradeDirection): Trade direction (buy/sell).
        magic (int): Magic number for trade identification.
        entry_price (float): Entry price for the trade.
        stop_loss (float): Stop loss price.
        sl_as_pip (float): Stop loss in pips (priority over sl_as_pct).
        sl_as_pct (float): Stop loss as percentage.
        take_profits (list[TakeProfit]): List of take profit levels. (close_pct can be min 0 and max 1, representing 0-100%)
        deviation (int): Maximum price deviation (0-100).
    """

    symbol: str
    volume: float = Field(..., gt=0, le=100)
    direction: str = Field(..., description="Trade direction (buy/sell)")
    magic: int = Field(default=None, ge=0)
    entry_price: float = Field(default=0.0, ge=0)
    stop_loss: float = Field(default=0.0, ge=0)
    sl_as_pip: float = Field(
        default=None,
        gt=0,
        le=1,
        description="Stop loss as pips, stop_loss is ignored if set. Takes priority over sl_as_pct",
    )
    sl_as_pct: float = Field(
        default=None,
        gt=0,
        le=1,
        description="Stop loss as percentage, stop_loss is ignored if set",
    )
    take_profits: list[TakeProfit] = Field(default_factory=list)
    deviation: int = Field(default=0, ge=0, le=100)
    comment: str = Field(
        default="DYNAMO", description="Trade comment. It cannot contain commas."
    )

    @field_validator("comment", mode="before")
    def remove_comma(cls, v):
        return v.replace(",", "_")
