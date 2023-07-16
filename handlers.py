import os

from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from api.steam import get_group_info
from database import (
    create_group,
    create_user,
    get_group_by_url,
    get_user,
    session,
)
from fsm import GroupStates
from keyboards import language_keyboard
from locales import get_user_language
from messages import send_groups_message, send_help

handlers = Router()


@handlers.message(Command("start", "language"))
async def start(message: types.Message) -> None:
    if message.text == "/start":
        create_user(message.from_user)

    await message.answer(
        "Выберите язык / Select language",
        reply_markup=language_keyboard(from_start=message.text == "/start"),
    )


@handlers.message(Command("help"))
async def help(message: types.Message):
    language = get_user_language(message.from_user.id)

    if not language:
        return await start(message)

    await send_help(message)


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


@handlers.message(Command("groups"))
async def groups(message: types.Message, state: FSMContext):
    await send_groups_message(message)
    await state.set_state(GroupStates.groups)


@handlers.message(Command("add_group"))
async def add_group(message: types.Message):
    if str(message.from_user.id) != os.getenv("ADMIN_ID"):
        return

    url, price = message.text.split(" ")[-2:]
    info = get_group_info(url)
    create_group(info, price)

    group = get_group_by_url(info.url)
    await message.answer_photo(
        types.URLInputFile(group.image),
        caption=str(group),
    )
