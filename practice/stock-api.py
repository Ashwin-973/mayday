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


def format_stock_response(stock):
    if stock["error"]:
        return (
            "I can't fetch live prices for this exchange with the free plan. "
            "Would you like to try NASDAQ instead?"
        )

    status = "Open" if stock["market_open"] else "Closed"

    return (
        f"{stock['name']} ({stock['symbol']}) is trading at "
        f"{stock['price']} {stock['currency']} on {stock['exchange']}.\n"
        f"Change today: {stock['percent_change']}%.\n"
        f"Market status: {status}."
    )

print(format_stock_response(get_stock_price("MSFT", "NASDAQ")))