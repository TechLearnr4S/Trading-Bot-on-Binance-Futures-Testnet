import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = TESTNET_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _post(self, endpoint: str, params: dict) -> dict:
        signed = self._sign(params)
        url = f"{self.base_url}{endpoint}"

        logger.debug("POST %s | params: %s", url, {k: v for k, v in signed.items() if k != "signature"})

        try:
            response = self.session.post(url, data=signed, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error when calling %s: %s", url, exc)
            raise ConnectionError(f"Could not reach Binance API: {exc}") from exc
        except requests.exceptions.Timeout:
            logger.error("Request to %s timed out", url)
            raise TimeoutError("Binance API request timed out. Try again.")

        logger.debug("Response [%s]: %s", response.status_code, response.text)

        data = response.json()

        if response.status_code != 200:
            code = data.get("code", response.status_code)
            msg = data.get("msg", response.text)
            logger.error("API error %s: %s", code, msg)
            raise RuntimeError(f"Binance API error {code}: {msg}")

        return data

    def get_account_info(self) -> dict:
        return self._post("/fapi/v2/account", {})

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None, stop_price: float = None) -> dict:
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity,
        }

        if order_type.upper() == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"
        elif order_type.upper() == "STOP":
            params["price"] = price
            params["stopPrice"] = stop_price
            params["timeInForce"] = "GTC"

        return self._post("/fapi/v1/order", params)
