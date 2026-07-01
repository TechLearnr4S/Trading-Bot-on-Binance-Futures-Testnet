import argparse
import logging
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceClient
from bot.logging_config import setup_logging
from bot.orders import (
    format_order_response,
    format_order_summary,
    place_limit_order,
    place_market_order,
    place_stop_limit_order,
)
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)

load_dotenv()
logger = logging.getLogger(__name__)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--symbol", required=True,
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side", required=True,
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type", dest="order_type", required=True,
        help="Order type: MARKET, LIMIT, or STOP",
    )
    parser.add_argument(
        "--quantity", required=True,
        help="Order quantity (in base asset units)",
    )
    parser.add_argument(
        "--price",
        help="Limit price (required for LIMIT and STOP orders)",
    )
    parser.add_argument(
        "--stop-price", dest="stop_price",
        help="Trigger price (required for STOP orders)",
    )
    return parser


def load_credentials() -> tuple[str, str]:
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    if not api_key or not api_secret:
        print(
            "Error: BINANCE_API_KEY and BINANCE_API_SECRET must be set.\n"
            "Create a .env file or export them as environment variables.",
            file=sys.stderr,
        )
        sys.exit(1)
    return api_key, api_secret


def run():
    setup_logging()
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)

        price = None
        stop_price = None

        if order_type in ("LIMIT", "STOP"):
            if not args.price:
                parser.error(f"--price is required for {order_type} orders.")
            price = validate_price(args.price)

        if order_type == "STOP":
            if not args.stop_price:
                parser.error("--stop-price is required for STOP orders.")
            stop_price = validate_price(args.stop_price)

    except ValueError as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        logger.error("Validation failed: %s", exc)
        sys.exit(1)

    request_params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }
    if price is not None:
        request_params["price"] = price
    if stop_price is not None:
        request_params["stop_price"] = stop_price

    print(format_order_summary(request_params))

    api_key, api_secret = load_credentials()
    client = BinanceClient(api_key=api_key, api_secret=api_secret)

    try:
        if order_type == "MARKET":
            response = place_market_order(client, symbol, side, quantity)
        elif order_type == "LIMIT":
            response = place_limit_order(client, symbol, side, quantity, price)
        elif order_type == "STOP":
            response = place_stop_limit_order(client, symbol, side, quantity, price, stop_price)
    except (RuntimeError, ConnectionError, TimeoutError) as exc:
        print(f"\nFailed to place order: {exc}", file=sys.stderr)
        logger.error("Order failed: %s", exc)
        sys.exit(1)

    print(format_order_response(response))
    print("\n✓ Order placed successfully.")
    logger.info("CLI session completed for %s %s %s", order_type, side, symbol)


if __name__ == "__main__":
    run()
