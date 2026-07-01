# Trading Bot — Binance Futures Testnet

A command-line trading bot for placing **Market**, **Limit**, and **Stop-Limit** orders on the [Binance Futures Testnet](https://testnet.binancefuture.com) (USDT-M perpetuals).

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper (signing, HTTP)
│   ├── orders.py          # Order placement logic and output formatters
│   ├── validators.py      # Input validation with clear error messages
│   └── logging_config.py  # Rotating file + console log handler setup
├── cli.py                 # CLI entry point (argparse)
├── .env.example           # Credential template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet API Credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com) and sign in with GitHub.
2. Navigate to **API Key** section and generate a key pair.
3. Copy the **API Key** and **Secret Key**.

### 2. Clone and Install

```bash
git clone <your-repo-url>
cd trading_bot

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your testnet keys:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

> **Never commit `.env` to version control.** It is already in `.gitignore`.

---

## How to Run

All commands are run from the project root directory.

### Place a Market Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Place a Limit Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 50000
```

### Place a Stop-Limit Order (Bonus)

```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.01 --price 49000 --stop-price 49500
```

### Arguments

| Argument       | Required            | Description                                         |
|----------------|---------------------|-----------------------------------------------------|
| `--symbol`     | Yes                 | USDT-M futures symbol, e.g. `BTCUSDT`, `ETHUSDT`   |
| `--side`       | Yes                 | `BUY` or `SELL`                                     |
| `--type`       | Yes                 | `MARKET`, `LIMIT`, or `STOP`                        |
| `--quantity`   | Yes                 | Order size in base asset units                      |
| `--price`      | For LIMIT and STOP  | Limit execution price                               |
| `--stop-price` | For STOP only       | Trigger price for the stop condition                |

---

## Sample Output

```
--- Order Request ---
  symbol      : BTCUSDT
  side        : BUY
  type        : MARKET
  quantity    : 0.01

--- Order Response ---
  Order ID      : 3713190475
  Symbol        : BTCUSDT
  Side          : BUY
  Type          : MARKET
  Status        : FILLED
  Orig Qty      : 0.01
  Executed Qty  : 0.01
  Avg Price     : 43215.60000

✓ Order placed successfully.
```

---

## Logging

All API requests and responses are logged to `logs/trading_bot.log` with timestamps.  
The log file rotates at 5 MB and keeps the last 3 files.

```
2025-01-15 14:32:10 | DEBUG    | bot.client | POST https://testnet.binancefuture.com/fapi/v1/order | params: {symbol: BTCUSDT, side: BUY, ...}
2025-01-15 14:32:11 | DEBUG    | bot.client | Response [200]: {"orderId": 3713190475, ...}
2025-01-15 14:32:11 | INFO     | bot.orders | MARKET order placed successfully | orderId=3713190475
```

---

## Assumptions

- Only **USDT-M perpetual futures** symbols are supported (must end in `USDT`).
- Quantity precision depends on the symbol's trading rules on Binance. If you receive a precision error, adjust your quantity accordingly (e.g., `0.001` instead of `0.0012345`).
- STOP orders use Binance's `STOP` type (stop-limit), which requires both a `--price` (limit) and `--stop-price` (trigger).
- Credentials are loaded from `.env` or environment variables at startup.

---

## Error Handling

| Scenario                    | Behavior                                           |
|-----------------------------|----------------------------------------------------|
| Missing/invalid credentials | Exits with a clear message before any API call     |
| Invalid symbol format       | Validation error printed to stderr, exits          |
| API error response          | Error code and message logged and printed          |
| Network timeout             | Friendly timeout message, exits with code 1        |
| Missing required arguments  | argparse prints usage hint automatically           |
