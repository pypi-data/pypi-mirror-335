from dataclasses import dataclass
from typing import Optional

from dmtapi.decorators import check_provided_access_token
from dmtapi.models.account_model import TraderInfo
from dmtapi.models.deal_model import TradeDeal
from dmtapi.models.order_model import TradeOrder
from dmtapi.models.position_model import Position
from dmtapi.models.symbol_model import SymbolInfoTick, SymbolInfo
from dmtapi.models.trade_model import TradeSetup
from dmtapi.req import RequestMaker


@dataclass
class APIConfig:
    """Configuration class to hold API settings"""

    api_key: str
    api_base_url: str
    access_token: Optional[str] = None


class BaseAPI(RequestMaker):
    """Base class for all API endpoints"""

    def __init__(self, config: APIConfig):
        super().__init__(config.api_base_url)
        self._config = config

    @property
    def api_key(self) -> str:
        return self._config.api_key

    @property
    def access_token(self) -> Optional[str]:
        return self._config.access_token


class AccountInfoApi(BaseAPI):
    @check_provided_access_token
    async def info(
        self,
        *,
        access_token: Optional[str] = None,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> TraderInfo:
        """
        Retrieve information about a specific trading account.

        Args:
            access_token (Optional[str]): Account access token. Required if login and server are not provided.
            login (Optional[str]): Account login. Required if access_token is not provided.
            server (Optional[str]): Trading server. Required if access_token is not provided.
            api_key (Optional[str]): Override default API key.

        Returns:
            TraderInfo: Object containing account information.

        Raises:
            ValueError: If neither access_token nor both login and server are provided.
        """

        r = await self.get(
            path="/account/info",
            access_token=access_token or self.access_token,
            login=login,
            server=server,
            api_key=api_key or self.api_key,
        )

        return TraderInfo(**r)

    async def all(self, *, api_key: Optional[str] = None) -> list[TraderInfo]:
        """
        Retrieve information about all available trading accounts.

        Args:
            api_key (Optional[str]): Override default API key.

        Returns:
            list[TraderInfo]: List of objects containing account information.

        Raises:
            ValueError: If neither api_key nor self.api_key is provided.
        """
        if not api_key and not self.api_key:
            raise ValueError("API key is required to access all accounts")

        r = await self.get(path="/account/all", api_key=api_key or self.api_key)

        return [TraderInfo(**i) for i in r]


class SymbolApi(BaseAPI):
    @check_provided_access_token
    async def price(
        self,
        *,
        symbol: str,
        access_token: Optional[str] = None,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> SymbolInfoTick:
        """
        Get the current price of a symbol.

        Args:
            symbol (str): Symbol name.
            access_token (Optional[str]): Account access token. Required if login and server are not provided.
            login (Optional[str]): Account login. Required if access_token is not provided.
            server (Optional[str]): Trading server. Required if access_token is not provided.
            api_key (Optional[str]): Override default API key.

        Returns:
            SymbolInfoTick: Symbol price information.
        """

        r = await self.get(
            path="/symbol/price",
            access_token=access_token or self.access_token,
            login=login,
            server=server,
            api_key=api_key or self.api_key,
            params={"symbol": symbol},
        )

        return SymbolInfoTick(**r)

    @check_provided_access_token
    async def info(
        self,
        *,
        symbol: str,
        access_token: Optional[str] = None,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> SymbolInfo:
        """
        Get information about a symbol.

        Args:
            symbol (str): Symbol name.
            access_token (Optional[str]): Account access token. Required if login and server are not provided.
            login (Optional[str]): Account login. Required if access_token is not provided.
            server (Optional[str]): Trading server. Required if access_token is not provided.
            api_key (Optional[str]): Override default API key.

        Returns:
            SymbolInfo: Symbol information.
        """

        r = await self.get(
            path="/symbol/info",
            access_token=access_token or self.access_token,
            login=login,
            server=server,
            api_key=api_key or self.api_key,
            params={"symbol": symbol},
        )

        return SymbolInfo(**r)

    @check_provided_access_token
    async def all(
        self,
        *,
        access_token: Optional[str] = None,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> list[str]:
        """
        Get information about all available symbols.

        Args:
            access_token (Optional[str]): Account access token. Required if login and server are not provided.
            login (Optional[str]): Account login. Required if access_token is not provided.
            server (Optional[str]): Trading server. Required if access_token is not provided.
            api_key (Optional[str]): Override default API key.

        Returns:
            list[dict]: List of symbol information.
        """

        r = await self.get(
            path="/symbol/all",
            access_token=access_token or self.access_token,
            login=login,
            server=server,
            api_key=api_key or self.api_key,
        )

        return r


class TradeApi(BaseAPI):
    @check_provided_access_token
    async def open(
        self,
        *,
        setup: TradeSetup,
        access_token: str,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> list[dict]:
        """
        Open a new trade based on the provided setup.

        Args:
            setup (TradeSetup): Trade configuration including symbol, volume, direction, etc.
            access_token (str): Account access token.
            login (int): Account login number.
            server (str): Trading server.
            api_key (Optional[str]): Override default API key.

        Returns:
            list[dict]: List of trade results.
            If you have multiple tp it returns multiple trades as MT5 doesn't support more than one tp on a trade.
            So it splits the volume and opens multiple trades with the same entry, sl and tp.
        """

        r = await self.post(
            path="/trade/open",
            access_token=access_token or self.access_token,
            login=login,
            server=server,
            api_key=api_key or self.api_key,
            data=setup.model_dump_json(),
        )

        return r

    @check_provided_access_token
    async def close(
        self,
        *,
        ticket: int,
        volume: float = None,
        access_token: Optional[str] = None,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Close an open position by ticket number. Enter volume for partial close.

        Args:
            ticket (int): Ticket number of the position to close.
            volume (float): Volume to close. If not provided, the entire position will be closed.
            access_token (Optional[str]): Account access token. Required if login and server are not provided.
            login (Optional[str]): Account login. Required if access_token is not provided.
            server (Optional[str]): Trading server. Required if access_token is not provided.
            api_key (Optional[str]): Override default API key.

        Returns:
            dict: Response from the server.

        Raises:
            ValueError: If it fails to close the position.
        """

        r = await self.get(
            path="/trade/close",
            access_token=access_token or self.access_token,
            login=login,
            server=server,
            api_key=api_key or self.api_key,
            params={"ticket": ticket, "volume": str(volume)},
        )

        return r

    @check_provided_access_token
    async def cancel(
        self,
        *,
        ticket: int,
        access_token: Optional[str] = None,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Cancel a pending order by ticket number

        Args:
            ticket (int): Ticket number of the pending order to cancel.
            access_token (Optional[str]): Account access token. Required if login and server are not provided.
            login (Optional[str]): Account login. Required if access_token is not provided.
            server (Optional[str]): Trading server. Required if access_token is not provided.
            api_key (Optional[str]): Override default API key.

        Returns:
            dict: Response from the server.

        Raises:
            ValueError: If it fails to cancel the pending order.
        """

        r = await self.get(
            path="/trade/cancel",
            access_token=access_token or self.access_token,
            login=login,
            server=server,
            api_key=api_key or self.api_key,
            params={"ticket": str(ticket)},
        )

        return r

    @check_provided_access_token
    async def modify(
        self,
        *,
        ticket: int,
        price_tp: Optional[float] = 0.0,
        price_sl: Optional[float] = 0.0,
        volume: Optional[float] = 0.0,
        access_token: Optional[str] = None,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Modify an existing trade by ticket number.
        To edit the entry you need to cancel the trade and open a new one.

        Args:
            ticket (int): Ticket number of the trade to modify.
            price_tp (float): New take profit price.
            price_sl (float): New stop loss price.
            volume (float): New trade volume.
            access_token (Optional[str]): Account access token. Required if login and server are not provided.
            login (Optional[str]): Account login. Required if access_token is not provided.
            server (Optional[str]): Trading server. Required if access_token is not provided.
            api_key (Optional[str]): Override default API key.

        Returns:
            dict: Response from the server.

        Raises:
            ValueError: If it fails to modify the trade.
        """

        if not price_tp and not price_sl and not volume:
            raise ValueError(
                "At least one of price_tp, price_sl, or volume must be provided"
            )

        r = await self.post(
            path="/trade/modify",
            access_token=access_token or self.access_token,
            login=login,
            server=server,
            api_key=api_key or self.api_key,
            data={
                "ticket": ticket,
                "price_tp": price_tp,
                "price_sl": price_sl,
                "volume": volume,
            },
        )

        return r


class OrderApi(BaseAPI):
    @check_provided_access_token
    async def history(
        self,
        *,
        access_token: Optional[str] = None,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> list[TradeDeal]:
        """
        Get the history of trades for a specific account.

        Args:
            access_token (Optional[str]): Account access token. Required if login and server are not provided.
            login (Optional[str]): Account login. Required if access_token is not provided.
            server (Optional[str]): Trading server. Required if access_token is not provided.
            api_key (Optional[str]): Override default API key.

        Returns:
            list[TradeDeal]: List of trade history.
        """

        r = await self.get(
            path="/deals/history",
            access_token=access_token or self.access_token,
            login=login,
            server=server,
            api_key=api_key or self.api_key,
        )

        return [TradeDeal(**i) for i in r]

    @check_provided_access_token
    async def pending(
        self,
        *,
        access_token: Optional[str] = None,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> list[TradeOrder]:
        """
        Get the history of trades for a specific account.

        Args:
            access_token (Optional[str]): Account access token. Required if login and server are not provided.
            login (Optional[str]): Account login. Required if access_token is not provided.
            server (Optional[str]): Trading server. Required if access_token is not provided.
            api_key (Optional[str]): Override default API key.

        Returns:
            list[TradeOrder]: List of trade history.
        """

        r = await self.get(
            path="/orders/pending",
            access_token=access_token or self.access_token,
            login=login,
            server=server,
            api_key=api_key or self.api_key,
        )

        return [TradeOrder(**i) for i in r]

    @check_provided_access_token
    async def positions(
        self,
        *,
        access_token: Optional[str] = None,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> list[Position]:
        """
        Get the history of trades for a specific account.

        Args:
            access_token (Optional[str]): Account access token. Required if login and server are not provided.
            login (Optional[str]): Account login. Required if access_token is not provided.
            server (Optional[str]): Trading server. Required if access_token is not provided.
            api_key (Optional[str]): Override default API key.

        Returns:
            list[Position]: List of trade history.
        """

        r = await self.get(
            path="/orders/open",
            access_token=access_token or self.access_token,
            login=login,
            server=server,
            api_key=api_key or self.api_key,
        )

        return [Position(**i) for i in r]


class DMTAPI:
    """
    Main class for interacting with the DMT trading API.

    This class provides methods to manage trading accounts and execute trades.

    Args:
        api_key (str): The API key for authentication.
        api_base_url (str): The base URL for the API.
        access_token (Optional[str]): The access token for the account.
    """

    def __init__(
        self,
        api_key: str,
        api_base_url: str,
        access_token: Optional[str] = None,
    ):
        self._config = APIConfig(
            api_key=api_key, api_base_url=api_base_url, access_token=access_token
        )

        self.account = AccountInfoApi(self._config)
        self.trade = TradeApi(self._config)
        self.order = OrderApi(self._config)
        self.symbol = SymbolApi(self._config)

    @property
    def api_key(self) -> str:
        return self._config.api_key

    @api_key.setter
    def api_key(self, value: str):
        self._config.api_key = value

    @property
    def access_token(self) -> Optional[str]:
        return self._config.access_token

    @access_token.setter
    def access_token(self, value: Optional[str]):
        self._config.access_token = value
