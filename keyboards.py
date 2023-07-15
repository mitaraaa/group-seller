from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from emoji import emojize

from database.models import Group
from fluent.runtime import FluentLocalization


class Language(str, Enum):
    ru = "ru"
    en = "en"


class LanguageAction(CallbackData, prefix="set_lang"):
    language: Language
    from_start: bool


class GroupsAction(CallbackData, prefix="select_group"):
    group_id: int


class ContinueAction(CallbackData, prefix="continue"):
    pass


def language_keyboard(from_start: bool = False):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=emojize(":Russia: RU"),
        callback_data=LanguageAction(
            language=Language.ru, from_start=from_start
        ),
    )
    builder.button(
        text=emojize(":United_States: EN"),
        callback_data=LanguageAction(
            language=Language.en, from_start=from_start
        ),
    )

    return builder.as_markup()


def continue_keyboard(language: FluentLocalization):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=emojize(language.format_value("continue")),
        callback_data=ContinueAction(),
    )

    return builder.as_markup()


def group_keyboard(groups: list[Group]):
    builder = InlineKeyboardBuilder()
    for group in groups:
        builder.button(
            text=group.name,
            callback_data=GroupsAction(group_id=group.id),
        )

    return builder.as_markup()
