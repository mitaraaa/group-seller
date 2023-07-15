import asyncio
import os

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters.command import Command
from fluent.runtime import FluentLocalization, FluentResourceLoader

from keyboards import LanguageAction, language_keyboard

router = Router()


loader = FluentResourceLoader("locales/{locale}")
en = FluentLocalization(["en"], ["main.ftl"], loader)
ru = FluentLocalization(["ru"], ["main.ftl"], loader)

language = None


@router.message(Command("start", "language"))
async def set_language(message: types.Message) -> None:
    await message.reply(
        "Выберите язык / Select language",
        reply_markup=language_keyboard(),
    )


@router.callback_query(LanguageAction.filter())
async def send_instructions(
    callback: types.CallbackQuery, callback_data: LanguageAction
):
    language = en if callback_data.language.value == "en" else ru

    await callback.message.answer(
        language.format_value("instruction"),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


async def main():
    dp = Dispatcher()
    dp.include_router(router)

    bot = Bot(token=os.getenv("BOT_TOKEN", ""))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
