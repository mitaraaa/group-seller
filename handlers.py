import os

from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from emoji import emojize

from api.steam import get_group_info
from database import (
    create_group,
    create_user,
    get_all_groups,
    get_group_by_url,
    get_user,
    session,
)
from database.db import get_group_by_id
from fsm import GroupStates
from keyboards import (
    BackAction,
    ContinueAction,
    GroupsAction,
    LanguageAction,
    continue_keyboard,
    group_keyboard,
    groups_keyboard,
    language_keyboard,
)
from locales import get_user_language, set_user_language

handlers = Router()


@handlers.message(Command("start", "language"))
async def start(message: types.Message) -> None:
    if message.text == "/start":
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
        await send_help(callback)


async def send_group_message(callback: types.CallbackQuery, group_id: int):
    language = get_user_language(callback.from_user.id)
    group = get_group_by_id(group_id)

    await callback.message.answer_photo(
        types.URLInputFile(group.image),
        caption=language.format_value(
            "group_info",
            {
                "link": f"https://steamcommunity.com/groups/{group.url}",
                "name": group.name,
                "tag": group.tag,
                "url": group.url,
                "founded": group.founded,
            },
        ),
        parse_mode="HTML",
        reply_markup=group_keyboard(language, group_id),
    )


async def send_help(context: types.CallbackQuery | types.Message):
    image = types.URLInputFile(
        "https://res.cloudinary.com/dhsnr66jg"
        "/image/upload/v1689409862/help_steam_groups.jpg"
    )

    language = get_user_language(context.from_user.id)

    if (not language) and isinstance(context, types.Message):
        return await start(context)

    continue_button = (
        continue_keyboard(language)
        if isinstance(context, types.CallbackQuery)
        else None
    )

    context = (
        context if isinstance(context, types.Message) else context.message
    )

    await context.answer_photo(
        image,
        caption=language.format_value("instruction"),
        reply_markup=continue_button,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


async def send_groups_message(context: types.CallbackQuery | types.Message):
    language = get_user_language(context.from_user.id)

    context = (
        context if isinstance(context, types.Message) else context.message
    )

    await context.answer(
        text=language.format_value("choosing_group"),
        reply_markup=groups_keyboard(get_all_groups()),
    )


@handlers.callback_query(GroupsAction.filter())
async def group(
    callback: types.CallbackQuery,
    callback_data: GroupsAction,
    state: FSMContext,
):
    await send_group_message(callback, callback_data.group_id)

    await state.set_state(GroupStates.group)


@handlers.callback_query(ContinueAction.filter())
async def continue_to_groups(callback: types.CallbackQuery, state: FSMContext):
    await send_groups_message(callback)
    await state.set_state(GroupStates.groups)


@handlers.callback_query(BackAction.filter())
async def back(callback: types.CallbackQuery, callback_data: BackAction):
    state = getattr(GroupStates, callback_data.action)
    if state == GroupStates.group:
        await send_group_message(callback, callback_data.group_id)
    elif state == GroupStates.groups:
        await send_groups_message(callback)


@handlers.message(Command("help"))
async def help(message: types.Message):
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
