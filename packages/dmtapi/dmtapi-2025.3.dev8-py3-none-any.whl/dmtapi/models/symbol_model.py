from pydantic import BaseModel, Field


class SymbolInfoTick(BaseModel):
    symbol: str = Field(..., title="Symbol")
    ask: float
    bid: float
    last: float
    time: int
    volume: int
    volume_real: float


class SymbolInfoLess(BaseModel):
    symbol: str = Field(..., description="Symbol name")
    ask: float
    askhigh: float
    asklow: float
    bid: float
    bidhigh: float
    bidlow: float
    last: float
    path: str
    volume: int
    volume_real: float
    time: int
    digits: int


class SymbolInfo(SymbolInfoLess):
    bank: str
    basis: str
    category: str
    chart_mode: int
    currency_base: str
    currency_margin: str
    currency_profit: str
    custom: bool
    description: str
    exchange: str
    expiration_mode: int
    expiration_time: int
    filling_mode: int
    formula: str
    isin: str
    lasthigh: float
    lastlow: float
    margin_hedged: float
    margin_initial: float
    margin_maintenance: float
    order_mode: int
    page: str
    point: float
    select: bool
    session_aw: float
    session_buy_orders: int
    session_buy_orders_volume: float
    session_close: float
    session_deals: int
    session_interest: float
    session_open: float
    session_price_limit_max: float
    session_price_limit_min: float
    session_price_settlement: float
    session_sell_orders: int
    session_sell_orders_volume: float
    session_turnover: float
    session_volume: float
    spread: int
    spread_float: bool
    start_time: int
    swap_long: float
    swap_mode: int
    swap_rollover3days: int
    swap_short: float
    ticks_bookdepth: int
    trade_accrued_interest: float
    trade_calc_mode: int
    trade_contract_size: float
    trade_exemode: int
    trade_face_value: float
    trade_freeze_level: int
    trade_liquidity_rate: float
    """
    `trade_mode` values:
        # mt5.SYMBOL_TRADE_MODE_xxx
        0: Disabled — the symbol is not available for trading | SYMBOL_TRADE_MODE_DISABLED
        1: Long only — only buy positions can be opened | SYMBOL_TRADE_MODE_LONGONLY
        2: Short only — only sell positions can be opened | SYMBOL_TRADE_MODE_SHORTONLY
        3: Close only — no new positions can be opened,
           only existing positions can be closed | SYMBOL_TRADE_MODE_CLOSEONLY
        4: Full access — the symbol is fully available for trading,
           allowing both buy and sell operations | SYMBOL_TRADE_MODE_FULL
    """
    trade_mode: int
    trade_stops_level: int
    trade_tick_size: float
    trade_tick_value: float
    trade_tick_value_loss: float
    trade_tick_value_profit: float
    visible: bool
    volume_limit: float
    volume_max: float
    volume_min: float
    volume_step: float
    volumehigh: int
    volumehigh_real: float
    volumelow: int
    volumelow_real: float
