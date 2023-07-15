import asyncio
import os

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters.command import Command
from emoji import emojize
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
    await message.answer(
        "Выберите язык / Select language",
        reply_markup=language_keyboard(from_start=message.text == "/start"),
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
    language = set_user_language(
        callback.from_user.id,
        callback_data.language,
        callback.from_user.first_name,
    )

    await callback.message.edit_text(
        emojize(language.format_value("language_set")),
    )

    if callback_data.from_start:
        await callback.message.answer(
            language.format_value("instruction"),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


@router.message(Command("help"))
async def help(message: types.Message):
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
