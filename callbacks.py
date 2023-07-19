from aiogram import Router, types
from emoji import emojize
from database import remove_order, get_group_by_id

from keyboards import (
    BackAction,
    ContinueAction,
    GroupAction,
    GroupViewAction,
    GroupsAction,
    LanguageAction,
)
from locales import set_user_language, get_user_language
from messages import (
    send_group_message,
    send_groups_message,
    send_help,
    send_order_message,
)

callbacks = Router()


@callbacks.callback_query(LanguageAction.filter())
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

    await callback.answer()


@callbacks.callback_query(GroupsAction.filter())
async def group(
    callback: types.CallbackQuery,
    callback_data: GroupsAction,
):
    await callback.message.delete()
    await send_group_message(callback, callback_data.group_id)

    await callback.answer()


@callbacks.callback_query(GroupAction.filter())
async def order(
    callback: types.CallbackQuery,
    callback_data: GroupAction,
):
    await send_order_message(callback, callback_data)
    await callback.answer()


@callbacks.callback_query(ContinueAction.filter())
async def continue_to_groups(callback: types.CallbackQuery):
    await send_groups_message(callback, from_continue=True)

    await callback.answer()


@callbacks.callback_query(BackAction.filter())
async def back(callback: types.CallbackQuery, callback_data: BackAction):
    await callback.message.delete()
    if callback_data.action == "remove_order":
        remove_order(callback_data.order_id)
    await send_groups_message(callback)
    await callback.answer()


@callbacks.callback_query(GroupViewAction.filter())
async def view(callback: types.CallbackQuery, callback_data: GroupViewAction):
    language = get_user_language(callback.from_user.id)
    group = get_group_by_id(callback_data.group_id)

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
        )
        + f"\n\n<code>{group.price} USD</code>",
    )
