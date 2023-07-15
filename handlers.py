import os
from aiogram import Router, types
from aiogram.filters.command import Command
from emoji import emojize
from api.steam import get_group_info
from database import (
    session,
    create_user,
    get_user,
    create_group,
    get_group_by_url,
)

from keyboards import LanguageAction, language_keyboard
from locales import get_user_language, set_user_language

handlers = Router()


@handlers.message(Command("start", "language"))
async def start(message: types.Message) -> None:
    create_user(message.from_user)

    await message.answer(
        "Выберите язык / Select language",
        reply_markup=language_keyboard(from_start=message.text == "/start"),
    )


@handlers.callback_query(LanguageAction.filter())
async def set_language(
    callback: types.CallbackQuery, callback_data: LanguageAction
):
    language = set_user_language(
        callback.from_user.id,
        callback_data.language,
    )

    await callback.message.edit_text(
        emojize(language.format_value("language_set")),
    )

    if callback_data.from_start:
        image = types.URLInputFile(
            "https://res.cloudinary.com/dhsnr66jg"
            "/image/upload/v1689409862/help_steam_groups.jpg"
        )
        await callback.message.answer_photo(
            image,
            caption=language.format_value("instruction"),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


@handlers.message(Command("help"))
async def help(message: types.Message):
    language = get_user_language(message.from_user.id)

    if not language:
        return await start(message)

    image = types.URLInputFile(
        "https://res.cloudinary.com/dhsnr66jg"
        "/image/upload/v1689409862/help_steam_groups.jpg"
    )
    await message.answer_photo(
        image,
        caption=language.format_value("instruction"),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@handlers.message(Command("profile"))
async def profile(message: types.Message):
    language = get_user_language(message.from_user.id)
    user = get_user(message.from_user.id)

    await message.answer(
        language.format_value(
            "profile",
            {
                "name": user.name,
                "id": user.id,
                "orders_amount": user.orders_amount(session),
                "orders_sum": user.orders_sum(session),
            },
        ),
        parse_mode="HTML",
    )


@handlers.message(Command("add_group"))
async def add_group(message: types.Message):
    if str(message.from_user.id) != os.getenv("ADMIN_ID"):
        return

    url = message.text.split(" ")[-1]
    info = get_group_info(url)
    create_group(info, 200)

    group = get_group_by_url(info.url)
    await message.answer_photo(
        types.URLInputFile(group.image), caption=str(group)
    )
