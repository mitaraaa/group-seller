import asyncio
import os

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters.command import Command
from fluent.runtime import FluentLocalization, FluentResourceLoader
from sqlalchemy import select

from database import session
from database.models import User
from keyboards import Language, LanguageAction, language_keyboard

router = Router()


loader = FluentResourceLoader("locales/{locale}")
en = FluentLocalization(["en"], ["main.ftl"], loader)
ru = FluentLocalization(["ru"], ["main.ftl"], loader)


@router.message(Command("start", "language"))
async def start(message: types.Message) -> None:
    await message.reply(
        "Выберите язык / Select language",
        reply_markup=language_keyboard(),
    )


def set_user_language(
    user_id: int, language: Language, first_name: str = None
) -> FluentLocalization:
    with session:
        stmt = select(User).where(User.id == user_id)
        user = session.scalar(stmt) or User(id=user_id, name=first_name)

        user.language = language.value

        session.add(user)
        session.commit()

    return en if language.value == "en" else ru


def get_user_language(user_id: int) -> FluentLocalization | None:
    with session:
        stmt = select(User).where(User.id == user_id)
        user = session.scalar(stmt)

        if not user:
            return None

        return en if user.language == "en" else ru


@router.callback_query(LanguageAction.filter())
async def set_language(
    callback: types.CallbackQuery, callback_data: LanguageAction
):
    set_user_language(
        callback.from_user.id,
        callback_data.language,
        callback.from_user.first_name,
    )


@router.message(Command("info"))
async def info(message: types.Message):
    language = get_user_language(message.from_user.id)

    if not language:
        await start(message)
        language = get_user_language(message.from_user.id)

    await message.answer(
        language.format_value("instruction"),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


async def main():
    dp = Dispatcher()
    dp.include_router(router)

    bot = Bot(token=os.getenv("BOT_TOKEN", ""))
    print("Started polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
