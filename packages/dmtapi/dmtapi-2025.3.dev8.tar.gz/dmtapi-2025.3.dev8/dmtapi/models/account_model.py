from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AccountStatusEnum(str, Enum):
    """
    Enumeration of possible account connection statuses.
    """

    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    DISCONNECTED = "disconnected"
    DISCONNECTED_2MIN = "disconnected_2min"
    DISCONNECTED_10MIN = "disconnected_10min"
    INVALID_CREDENTIALS = "invalid_credentials"


class TraderInfo(BaseModel):
    """
    Trading account information and status.

    Attributes:
        name (str): Account name.
        server (str): Trading server.
        login (int): Account login.
        server_type (str): Server type (default: "mt5").
        access_token (str): Access token.
        inception_date (datetime): Account creation date.
        starting_balance (float): Initial account balance.
        currency (str): Account currency.
        leverage (int): Account leverage.
        limit_orders (int): Maximum number of pending orders.
        margin_so_mode (int): Stop out mode.
        trade_allowed (bool): Whether trading is allowed.
        trade_expert (bool): Whether expert advisors are allowed.
        margin_mode (int): Margin calculation mode.
        currency_digits (int): Currency decimal places.
        fifo_close (bool): Whether FIFO rule is enabled.
        balance (float): Current balance.
        credit (float): Account credit.
        profit (float): Current floating profit/loss.
        equity (float): Current equity.
        margin (float): Used margin.
        margin_free (float): Free margin.
        margin_level (float): Margin level percentage.
        margin_so_call (float): Margin call level.
        margin_so_so (float): Stop out level.
        margin_initial (float): Initial margin requirement.
        margin_maintenance (float): Maintenance margin requirement.
        assets (float): Total assets.
        liabilities (float): Total liabilities.
        commission_blocked (float): Blocked commission amount.
        active (bool): Whether account is active.
        status (AccountStatusEnum): Account connection status.
    """

    name: str = Field("")
    server: str
    login: int
    server_type: str = Field("mt5")
    access_token: str
    inception_date: datetime
    starting_balance: float
    currency: str
    leverage: int
    limit_orders: int
    margin_so_mode: int
    trade_allowed: bool
    trade_expert: bool
    margin_mode: int
    currency_digits: int
    fifo_close: bool
    balance: float
    credit: float
    profit: float
    equity: float
    margin: float
    margin_free: float
    margin_level: float
    margin_so_call: float
    margin_so_so: float
    margin_initial: float
    margin_maintenance: float
    assets: float
    liabilities: float
    commission_blocked: float
    active: bool = False
    status: AccountStatusEnum = AccountStatusEnum.DISCONNECTED
