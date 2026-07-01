import re


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP"}
SYMBOL_PATTERN = re.compile(r"^[A-Z]{2,10}USDT$")


def validate_symbol(symbol: str) -> str:
    cleaned = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(cleaned):
        raise ValueError(
            f"'{symbol}' is not a valid USDT-M futures symbol. "
            "Expected format: BTCUSDT, ETHUSDT, etc."
        )
    return cleaned


def validate_side(side: str) -> str:
    normalized = side.strip().upper()
    if normalized not in VALID_SIDES:
        raise ValueError(
            f"'{side}' is not a valid side. Choose from: {', '.join(sorted(VALID_SIDES))}"
        )
    return normalized


def validate_order_type(order_type: str) -> str:
    normalized = order_type.strip().upper()
    if normalized not in VALID_ORDER_TYPES:
        raise ValueError(
            f"'{order_type}' is not a supported order type. "
            f"Choose from: {', '.join(sorted(VALID_ORDER_TYPES))}"
        )
    return normalized


def validate_quantity(quantity: str) -> float:
    try:
        value = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Quantity must be a number, got: '{quantity}'")
    if value <= 0:
        raise ValueError(f"Quantity must be greater than zero, got: {value}")
    return value


def validate_price(price: str) -> float:
    try:
        value = float(price)
    except (ValueError, TypeError):
        raise ValueError(f"Price must be a number, got: '{price}'")
    if value <= 0:
        raise ValueError(f"Price must be greater than zero, got: {value}")
    return value
