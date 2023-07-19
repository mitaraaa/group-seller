from aiogram import Router, types
from emoji import emojize

from keyboards import (
    BackAction,
    ContinueAction,
    GroupAction,
    GroupsAction,
    LanguageAction,
)
from locales import set_user_language
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
async def back(callback: types.CallbackQuery):
    await callback.message.delete()
    await send_groups_message(callback)
    await callback.answer()
