from io import BytesIO
import os

from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.utils.chat_action import ChatActionSender

from api.steam import get_group_info
from database import (
    create_group,
    create_user,
    get_group_by_url,
    get_user,
    session,
    get_user_by_username,
    get_all_groups,
)

from keyboards import groups_keyboard, language_keyboard, orders_keyboard
from locales import get_user_language
from messages import send_groups_message, send_help
from bot import bot

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
                "name": user.username,
                "id": user.id,
                "orders_amount": user.orders_amount(session),
                "orders_sum": user.orders_sum(session),
            },
        ),
    )


@handlers.message(Command("groups"))
async def groups(message: types.Message):
    if not get_user_language(message.from_user.id):
        return await start(message)

    await send_groups_message(message)


@handlers.message(Command("add_group"))
async def add_group(message: types.Message):
    if str(message.from_user.id) != os.getenv("ADMIN_ID"):
        return

    if len(message.text.split(" ")) != 3:
        await message.reply(
            "You need to provide correct Steam group link and price (in USD)"
        )
        return

    language = get_user_language(message.from_user.id, admin=True)

    url, price = message.text.split(" ")[-2:]
    info = get_group_info(url)
    create_group(info, price)

    group = get_group_by_url(info.url)
    await message.answer_photo(
        types.URLInputFile(group.image),
        caption="Added group:\n\n"
        + language(
            "group_info",
            {
                "link": f"https://steamcommunity.com/groups/{group.url}",
                "name": group.name,
                "tag": group.tag,
                "url": group.url,
                "founded": group.founded,
            },
        ),
    )


@handlers.message(Command("remove_group"))
async def remove_group(message: types.Message):
    if str(message.from_user.id) != os.getenv("ADMIN_ID"):
        return

    language = get_user_language(message.from_user.id, admin=True)
    keyboard = groups_keyboard(get_all_groups(), remove=True)
    if len(keyboard.inline_keyboard) == 0:
        await message.answer(text=language.format_value("empty_list_of_group"))
    else:
        await message.answer(
            text=language.format_value("select_to_remove"),
            reply_markup=(keyboard),
        )


@handlers.message(Command("add_groups"))
async def add_groups(message: types.Message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    result: BytesIO = await bot.download_file(file_path)
    async with ChatActionSender.upload_document(
        bot=bot, chat_id=message.chat.id
    ):
        count = 0
        for bline in result.readlines():
            try:
                line = bline.decode()
                url, price = line.split(" ")
                info = get_group_info(url)
                create_group(info, price)
                count += 1
            except:
                print("Skipped line")

        await message.reply(f"Loaded {count} groups.")


@handlers.message(Command("lookup"))
async def lookup(message: types.Message):
    if str(message.from_user.id) != os.getenv("ADMIN_ID"):
        return

    if len(message.text.split(" ")) != 2:
        await message.reply("You need to provide username (@username)")
        return

    language = get_user_language(message.from_user.id, admin=True)

    username = message.text.split(" ")[-1].removeprefix("@")
    user = get_user_by_username(username)

    if not user:
        await message.answer("No user found with such username")

    await message.answer(
        language.format_value(
            "profile",
            {
                "name": user.username,
                "id": user.id,
                "orders_amount": user.orders_amount(session),
                "orders_sum": user.orders_sum(session),
            },
        ),
        reply_markup=orders_keyboard(user.id),
    )
