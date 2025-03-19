# DESK Python SDK

A Python client for interacting with DESK Exchange API, featuring JWT authentication and EVM wallet integration.

## Features

- EVM wallet integration
- JWT-based authentication
- Subaccount management
- Type-safe API interactions
- Real-time WebSocket support
- Comprehensive error handling

## Installation

```bash
pip install desk-python-sdk
```
or
```bash
poetry add desk-python-sdk
```

## List of functions

### Info

```python
    subscribe
    disconnect_websocket
    get_market_info
    get_mark_price
    get_collaterals_info
    get_last_trades
    get_subaccount_summary
    get_current_funding_rate
    get_historical_funding_rates
    get_trade_history
```


### Exchange

```python
    place_order
    batch_place_order
    cancel_order
    batch_cancel_order
    cancel_all_orders
    deposit_collateral
    withdraw_collateral
```


## Usage

### Initialize the Client

```python
from desk.auth import Auth
from desk.exchange import Exchange
from desk.info import Info

# Initialize authentication
auth = Auth(
    network="mainnet", # mainnet, testnet
    private_key="YOUR_PRIVATE_KEY",
    rpc_url="https://base-rpc.publicnode.com",
    account="YOUR_ACCOUNT_ADDRESS",
    sub_account_id=0
)

# Initialize exchange client
exchange = Exchange(
    network="mainnet", # mainnet, testnet
    auth=auth
)

# Initialize info client
info = Info(
    network="mainnet", # mainnet, testnet
    skip_ws=False
)
```

### Account Management

```python
# Get account information
account_summary = info.get_subaccount_summary(account="YOUR_ACCOUNT", sub_account_id=0)

# Get funding rates info
funding_rates = info.get_current_funding_rate("BTCUSD")
```

### Trading Operations

```python
from desk.enum import OrderSide, OrderType, TimeInForce, MarketSymbol

# Place a limit order
limit_order = exchange.place_order(
    symbol=MarketSymbol.BTCUSD,
    amount="0.001",
    price="99714.4",
    side=OrderSide.LONG,
    order_type=OrderType.LIMIT,
    time_in_force=TimeInForce.GTC,
    wait_for_reply=True
)

# Place a market order
market_order = exchange.place_order(
    symbol=MarketSymbol.BTCUSD,
    amount="0.001",
    price="92123.4",
    side=OrderSide.SHORT,
    order_type=OrderType.MARKET,
    wait_for_reply=True
)

# Cancel an order
exchange.cancel_order(
    symbol=MarketSymbol.BTCUSD,
    order_digest="ORDER_DIGEST",
    is_conditional_order=False,
    wait_for_reply=True
)

# Batch manage orders
exchange.batch_place_orders(
    orders=[
        {
            "symbol": "BTCUSD",
            "amount": "0.001",
            "price": "92123.4",
            "side": OrderSide.LONG,
            "order_type": OrderType.LIMIT,
            "time_in_force": TimeInForce.GTC
        },
        {
            "symbol": "BTCUSD",
            "amount": "0.001",
            "price": "92123.4",
            "side": OrderSide.SHORT,
            "order_type": OrderType.LIMIT,
            "time_in_force": TimeInForce.GTC
        }
    ]
)

# Batch Cancel Specific Orders
exchange.batch_cancel_order(
    orders=[
        {
            "symbol": "BTCUSD",
        },
        {
            "symbol": "ETHUSD",
            "order_digest": "ORDER_DIGEST"
        }
    ]
)

# Cancel all orders
exchange.cancel_all_orders(
    symbol=MarketSymbol.BTCUSD,
    is_conditional_order=False,
    wait_for_reply=True
)
```

### WebSocket Streams

```python
from desk.enum import Subscription, MarketSymbol

# Subscribe to mark prices
info.subscribe(
    {"type": Subscription.MARK_PRICE}
    lambda x: print("markprice: ", x['data'])
)

# Subscribe to orderbook
info.subscribe(
    {"type": Subscription.ORDERBOOK, "symbol": MarketSymbol.BTCUSD},
    lambda x: print("orderbook: ", x['data'])
)
```

## Running examples

```python
python examples/manage_order.py
python examples/get_info.py
python examples/deposit_withdraw.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

See the [Contributor Guide](CONTRIBUTING.md) for more details.

## License

MIT License - see the [LICENSE](LICENSE) file for details.
