import requests

TWELVE_API_KEY = ""

def get_stock_price(symbol, exchange=None):
    params = {
        "symbol": symbol,
        "apikey": TWELVE_API_KEY
    }
    if exchange:
        params["exchange"] = exchange

    r = requests.get("https://api.twelvedata.com/quote", params=params)
    data = r.json()

    # Handle API-level errors
    if data.get("status") == "error":
        return {
            "error": True,
            "message": data.get("message", "Stock data unavailable")
        }

    return {
        "error": False,
        "symbol": data["symbol"],
        "name": data["name"],
        "price": data["close"],
        "currency": data["currency"],
        "exchange": data["exchange"],
        "percent_change": data["percent_change"],
        "market_open": data["is_market_open"]
    }

print(get_stock_price("RELIANCE", "NSE"))