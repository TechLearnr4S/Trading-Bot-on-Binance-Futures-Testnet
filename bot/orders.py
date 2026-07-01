import logging

from bot.client import BinanceClient

logger = logging.getLogger(__name__)


def place_market_order(client: BinanceClient, symbol: str, side: str, quantity: float) -> dict:
    logger.info(
        "Placing MARKET %s order | symbol=%s qty=%s",
        side, symbol, quantity,
    )
    response = client.place_order(
        symbol=symbol,
        side=side,
        order_type="MARKET",
        quantity=quantity,
    )
    logger.info("MARKET order placed successfully | orderId=%s", response.get("orderId"))
    return response


def place_limit_order(client: BinanceClient, symbol: str, side: str, quantity: float, price: float) -> dict:
    logger.info(
        "Placing LIMIT %s order | symbol=%s qty=%s price=%s",
        side, symbol, quantity, price,
    )
    response = client.place_order(
        symbol=symbol,
        side=side,
        order_type="LIMIT",
        quantity=quantity,
        price=price,
    )
    logger.info("LIMIT order placed successfully | orderId=%s", response.get("orderId"))
    return response


def place_stop_limit_order(client: BinanceClient, symbol: str, side: str, quantity: float, price: float, stop_price: float) -> dict:
    logger.info(
        "Placing STOP %s order | symbol=%s qty=%s price=%s stopPrice=%s",
        side, symbol, quantity, price, stop_price,
    )
    response = client.place_order(
        symbol=symbol,
        side=side,
        order_type="STOP",
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )
    logger.info("STOP order placed successfully | orderId=%s", response.get("orderId"))
    return response


def format_order_summary(params: dict) -> str:
    lines = ["\n--- Order Request ---"]
    for key, value in params.items():
        lines.append(f"  {key:<12}: {value}")
    return "\n".join(lines)


def format_order_response(response: dict) -> str:
    fields = [
        ("orderId", "Order ID"),
        ("symbol", "Symbol"),
        ("side", "Side"),
        ("type", "Type"),
        ("status", "Status"),
        ("origQty", "Orig Qty"),
        ("executedQty", "Executed Qty"),
        ("avgPrice", "Avg Price"),
        ("price", "Limit Price"),
        ("stopPrice", "Stop Price"),
    ]

    lines = ["\n--- Order Response ---"]
    for field, label in fields:
        value = response.get(field)
        if value not in (None, "", "0", "0.00000000"):
            lines.append(f"  {label:<14}: {value}")
    return "\n".join(lines)
