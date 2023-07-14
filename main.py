import os
from aiogram import Bot, Dispatcher, executor, types
from fluent.runtime import FluentLocalization, FluentResourceLoader

from keyboards import LANGUAGE_KEYBOARD, language_callback

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)


loader = FluentResourceLoader("locales/{locale}")
en = FluentLocalization(["en"], ["main.ftl"], loader)
ru = FluentLocalization(["ru"], ["main.ftl"], loader)

language = None


@dp.message_handler(commands=["start", "language"])
async def set_language(message: types.Message):
    await message.reply(
        "Выберите язык / Select language",
        reply_markup=LANGUAGE_KEYBOARD,
    )


@dp.callback_query_handler(language_callback.filter())
async def send_instructions(
    callback: types.CallbackQuery, callback_data: dict
):
    language = en if callback_data["language"] == "EN" else ru
    await bot.send_message(
        callback.message.chat.id,
        language.format_value("instruction"),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
