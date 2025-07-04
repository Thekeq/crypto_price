# 📊 Telegram Crypto Coin Price Bot

👉 [Читать на русском](README.ru.md)

A simple Telegram bot for tracking cryptocurrency prices using the  
[CoinMarketCap API](https://coinmarketcap.com/api/)

## 🔧 Features

- 📈 Check the price of a coin: `/price`
- ⭐ Add a coin to favorites: `/fav`
- 📋 View favorite coins: `/list_fav`
- ❌ Remove a coin from favorites: `/remove_fav`
- 🌐 Change bot language: `/language`
- ℹ️ Bot info: `/start`
- 🔍 Inline query support (type coin symbol in any chat)

## 🖼️ Example

![Screenshot](exampleprice.jpg)

## 🚀 Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/thekeq/crypto_price.git
    cd crypto_price
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Rename `.env.example` to `.env` and add your tokens:

    ```env
    BOT_TOKEN=your_telegram_bot_token
    COINCAP_API=your_api_key
    ```

4. Set up inline mode with BotFather:

    ```
    /setinline
    @your_bot
    Enter a coin symbol (e.g. BTC, ETH)
    ```

5. Run the bot:

    ```bash
    python main.py
    ```

## 📦 Dependencies

- Python 3.10+
- `aiogram`
- `requests`
- `python-dotenv`

---

💬 Need help? Feel free to reach out!
