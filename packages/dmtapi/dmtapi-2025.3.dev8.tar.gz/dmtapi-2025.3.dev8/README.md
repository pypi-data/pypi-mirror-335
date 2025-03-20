# DMTAPI

A comprehensive Python package for managing trading accounts and executing trades through a unified API interface. This
package provides an asynchronous interface for interacting with trading platforms.

[![PyPI version](https://badge.fury.io/py/dmtapi.svg)](https://badge.fury.io/py/dmtapi)
[![Python versions](https://img.shields.io/pypi/pyversions/dmtapi.svg)](https://pypi.org/project/dmtapi/)

## Features

- Asynchronous API implementation
- Comprehensive trading account management
- Real-time symbol price information
- Trade execution with multiple take-profit levels
- Order and position tracking
- Detailed account information retrieval

## Installation

```bash
pip install dmtapi
```

## Quick Start

```python
from dmtapi import DMTAPI
from dmtapi.models.trade_model import TradeSetup, TakeProfit


async def main():
    # Initialize the API with your credentials
    api = DMTAPI(
        api_key="your_api_key",
        api_base_url="https://api.example.com"
    )

    # Get account information
    account_info = await api.account.info(
        access_token="your_access_token"
    )

    # Create and execute a trade
    setup = TradeSetup(
        symbol="EURUSD",
        volume=0.1,
        direction="buy",  # or "sell"
        stop_loss=1.0500,
        take_profits=[
            TakeProfit(price=1.0600, close_pct=1.0)
        ]
    )

    result = await api.trade.open(
        setup=setup,
        access_token="your_access_token"
    )

```

## API Structure

The DMTAPI is organized into several modules for different functionalities:

- `account`: Account management and information
- `symbol`: Symbol information and pricing
- `trade`: Trade execution and management
- `order`: Order history and position tracking

### Account Management

```python
# Get specific account information
account_info = await api.account.info(
    access_token="your_access_token"
)

# Get all accounts
all_accounts = await api.account.all()
```

### Symbol Operations

```python
# Get symbol price
price = await api.symbol.price(
    symbol="EURUSD",
    access_token="your_access_token"
)

# Get symbol information
symbol_info = await api.symbol.info(
    symbol="EURUSD",
    access_token="your_access_token"
)
```

### Trade Operations

```python
# Open a trade
result = await api.trade.open(
    setup=trade_setup,
    access_token="your_access_token"
)

# Close a position
result = await api.trade.close(
    ticket=12345,
    access_token="your_access_token"
)
```

### Order Management

```python
# Get position history
history = await api.order.history(
    access_token="your_access_token"
)

# Get pending orders
pending = await api.order.pending(
    access_token="your_access_token"
)

# Get open positions
positions = await api.order.positions(
    access_token="your_access_token"
)
```

## Authentication

The API supports two authentication methods:

1. Access Token Authentication:

```python
api = DMTAPI(
    api_key="your_api_key",
    api_base_url="https://api.example.com",
    access_token="your_access_token"
)
```

2. Login/Server Authentication:

```python
# Use login and server for specific requests
account_info = await api.account.info(
    login=12345,
    server="trading_server",
    api_key="your_api_key"
)
```

## Models

### TradeSetup

```python
from dmtapi.models.trade_model import TradeSetup, TakeProfit

setup = TradeSetup(
    symbol="EURUSD",  # Trading symbol
    volume=0.1,  # Trading volume
    direction="buy",  # Trade direction (buy/sell)
    stop_loss=1.0500,  # Stop loss price
    take_profits=[  # Multiple take profit levels
        TakeProfit(price=1.0600, close_pct=0.5),
        TakeProfit(price=1.0700, close_pct=0.5)
    ]
)
```

### TraderInfo

Provides comprehensive account information including:

- Account details (name, server, login)
- Balance and equity
- Margin information
- Account status

## Error Handling

The API uses standard Python exceptions for error handling:

```python
try:
    result = await api.trade.open(
        setup=trade_setup,
        access_token="your_access_token"
    )
except ValueError as e:
    print(f"Invalid parameters: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
```

## Examples

For more detailed examples, check the [examples](./examples) directory in the repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.