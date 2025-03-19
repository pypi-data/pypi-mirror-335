import enum

class OrderType(enum.Enum):
    LIMIT = "Limit"
    MARKET = "Market"
    STOP = "Stop"
    STOP_MARKET = "StopMarket"
    TAKE_PROFIT = "TakeProfit"
    TAKE_PROFIT_MARKET = "TakeProfitMarket"

class TimeInForce(enum.Enum):
    GTC = "GTC"
    FOK = "FOK"
    IOC = "IOC"
    POST_ONLY = "PostOnly"

class OrderSide(enum.Enum):
    LONG = "Long"
    SHORT = "Short"

class MarketSymbol(enum.Enum):
    BTCUSD = "BTCUSD"
    ETHUSD = "ETHUSD"
    SOLUSD = "SOLUSD"
    VIRTUALUSD = "VIRTUALUSD"
    KAITOUSD = "KAITOUSD"

class CollateralSymbol(enum.Enum):
    USDC = "USDC"

class Subscription(enum.Enum):
    TRADE = "tradesV2"
    ORDERBOOK = "l2BookV2"
    MARK_PRICE = "markPricesV2"
    ORDER_UPDATES = "orderUpdatesV2"
    POSITION_UPDATES = "positionUpdatesV2"
