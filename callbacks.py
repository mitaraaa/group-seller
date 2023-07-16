from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from emoji import emojize

from fsm import GroupStates
from keyboards import (
    BackAction,
    ContinueAction,
    GroupAction,
    GroupsAction,
    LanguageAction,
)
from locales import set_user_language
from messages import send_group_message, send_groups_message, send_help

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
    state: FSMContext,
):
    await send_group_message(callback, callback_data.group_id)

    await state.set_state(GroupStates.group)
    await callback.answer()


@callbacks.callback_query(GroupAction.filter())
async def order(
    callback: types.CallbackQuery,
    callback_data: GroupAction,
    state: FSMContext,
):
    await callback.answer()


@callbacks.callback_query(ContinueAction.filter())
async def continue_to_groups(callback: types.CallbackQuery, state: FSMContext):
    await send_groups_message(callback)

    await state.set_state(GroupStates.groups)
    await callback.answer()


@callbacks.callback_query(BackAction.filter())
async def back(callback: types.CallbackQuery, callback_data: BackAction):
    state = getattr(GroupStates, callback_data.action)
    if state == GroupStates.group:
        await send_group_message(callback, callback_data.group_id)
    elif state == GroupStates.groups:
        await send_groups_message(callback)

    await callback.answer()