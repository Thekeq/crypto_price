import requests
from dotenv import load_dotenv
import os

load_dotenv()

API = os.getenv("COINCAP_API")


def get_price(symbol, language="en"):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "X-CMC_PRO_API_KEY": API
    }
    params = {
        "symbol": symbol.upper(),
        "convert": "USD"
    }
    response = requests.get(url, headers=headers, params=params).json()

    try:
        data = response["data"][symbol.upper()]
        name = data["name"]
        price = data["quote"]["USD"]["price"]
        if price >= 1:
            formatted_price = f"${round(price, 2)}"
        elif price >= 0.01:
            formatted_price = f"${round(price, 4)}"
        else:
            formatted_price = f"${price:.8f}"
        return f"{name}: {formatted_price}"
    except Exception as e:
        return f"❌ Coin not found or invalid API key.\n{e}" if language == "en" \
            else f"❌ Монета не найдена или неверный API-Ключ\n{e}"


def get_prices(symbols: list[str], language="en"):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "X-CMC_PRO_API_KEY": API
    }
    params = {
        "symbol": ",".join([s.upper() for s in symbols]),
        "convert": "USD"
    }

    response = requests.get(url, headers=headers, params=params).json()

    prices = {}
    for symbol in symbols:
        try:
            data = response["data"][symbol.upper()]
            name = data["name"]
            price = data["quote"]["USD"]["price"]
            if price >= 1:
                formatted_price = f"${round(price, 2)}"
            elif price >= 0.01:
                formatted_price = f"${round(price, 4)}"
            else:
                formatted_price = f"${price:.8f}"
            prices[symbol.lower()] = f"{name}: {formatted_price}"
        except Exception as e:
            prices[symbol.lower()] = "❌ Not found" if language == "en" else "❌ Не найдена"
    return prices
