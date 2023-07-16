from aiogram import types
from database import get_group_by_id, get_all_groups
from keyboards import (
    continue_keyboard,
    group_keyboard,
    groups_keyboard,
)
from locales import get_user_language


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
