import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, \
    InputTextMessageContent, InlineQuery
from dotenv import load_dotenv
from db import DataBase
from api import get_price, get_prices
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
router = Router()
db = DataBase("data.db")


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id

    text_en = (
        "<b>📋 Commands:</b>\n"
        "/price — 📈 Check coin price\n"
        "/fav — ⭐ Add coin to favorites\n"
        "/list_fav — 📋 Favorite coins\n"
        "/remove_fav — ❌ Remove from favorites\n"
        "/language — 🌐 Change language\n"
        "/start — ℹ️ Bot information"
    )
    text_ru = (
        "<b>📋 Команды:</b>\n"
        "/price — 📈 Проверить цену монеты\n"
        "/fav — ⭐ Добавить в избранное\n"
        "/list_fav — 📋 Избранные монеты\n"
        "/remove_fav — ❌ Удалить из избранного\n"
        "/language — 🌐 Сменить язык\n"
        "/start — ℹ️ Информация о боте"
    )
    if not db.user_exists(user_id):  # Проверка на существование пользователя
        db.add_user(user_id, "en")
        await message.answer(text_en)

    else:
        await message.answer(text_ru if db.user_language(
            user_id) == "ru" else text_en)


@router.message(Command("language"))  # Смена языка
async def change_language(message: Message):
    user_id = message.from_user.id
    db.change_language(user_id)
    lang = db.user_language(user_id)
    await message.reply("Язык изменён!" if lang == "ru" else "Language changed! 🇺🇸")


@router.message(Command("price"))  # Отправляем монетку
async def send_coin_id(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if not db.user_exists(user_id):  # Проверка на существование пользователя
        db.add_user(user_id, "en")
        await message.answer("Enter a coin to check its price:")

    else:
        await message.answer("Введите монетку чтобы узнать цену: " if db.user_language(
            user_id) == "ru" else "Enter a coin to check its price:")

    await state.set_state("check_price")


@router.message(StateFilter("check_price"))  # Ловим сообщение и получаем цену
async def check_price(message: Message, state: FSMContext):
    user_id = message.from_user.id
    price = get_price(message.text, db.user_language(user_id))
    await message.reply(price)
    await state.clear()


class FavState(StatesGroup):
    waiting_for_coin = State()


@router.message(Command("fav"))  # Добавить в избранные
async def fav_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db.user_language(user_id)
    text = "Введите символ монеты, чтобы добавить в избранное (например, BTC):" if lang == "ru" else "Enter the coin symbol to add to favorites (e.g. BTC):"
    await message.answer(text)
    await state.set_state(FavState.waiting_for_coin)


@router.message(FavState.waiting_for_coin)  # Процесс добавления в избранные
async def add_favorite_coin(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db.user_language(user_id)
    coin = message.text.strip().lower()

    # Проверка монеты
    price = get_price(coin, lang)
    if "not found" in price.lower() or "не найдена" in price.lower():
        text = "Монета не найдена." if lang == "ru" else "Coin not found."
        await message.answer(text)
        return

    db.add_favorite(user_id, coin)

    text = f"{coin.upper()} добавлена в избранное!" if lang == "ru" else f"{coin.upper()} added to your favorites!"
    await message.answer(text)
    await state.clear()


@router.message(Command("list_fav"))  # Список избранных
async def list_favorites(message: Message):
    user_id = message.from_user.id
    lang = db.user_language(user_id)

    rows = db.get_favorites(user_id)
    if not rows:
        text = "У вас нет избранных монет." if lang == "ru" else "You have no favorite coins."
        await message.answer(text)
        return

    coins = [row[0] for row in rows]
    prices_dict = get_prices(coins, lang)

    lines = [prices_dict[c] for c in coins]

    title = "<b>Избранные монеты:</b>\n" if lang == "ru" else "<b>Your favorite coins:</b>\n"
    await message.answer(title + "\n".join(lines))


@router.message(Command("remove_fav"))  # Удалить из избранного
async def remove_favorite(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db.user_language(user_id)
    await message.answer(
        "Введите монету для удаления из избранного:" if lang == "ru" else "Enter the coin to remove from favorites:")
    await state.set_state("remove_coin")


@router.message(StateFilter("remove_coin"))  # Процесс удаления из избранного
async def remove_coin_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db.user_language(user_id)
    coin = message.text.lower()

    db.delete_favorite(user_id, coin)

    await message.answer("Удалено из избранного." if lang == "ru" else "Removed from favorites.")
    await state.clear()


@router.inline_query()  # Получаем цену из сообщения @bot coin
async def inline_query_handler(inline_query: InlineQuery):
    user_id = inline_query.from_user.id
    query = inline_query.query.strip().lower()

    if not query:
        return

    lang = db.user_language(user_id)
    price = get_price(query, lang)

    result_text = f"{price}"

    results = [
        InlineQueryResultArticle(
            id="1",
            title=f"Price of {query.upper()}" if lang == "en" else f"Цена {query.upper()}",
            input_message_content=InputTextMessageContent(message_text=result_text),
            description=price,
        )
    ]

    await inline_query.answer(results, cache_time=1)


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    print("Telegram Bot is running...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
