from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from emoji import emojize


class Language(str, Enum):
    ru = "ru"
    en = "en"


class LanguageAction(CallbackData, prefix="set_lang"):
    language: Language
    from_start: bool


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


def group_keyboard(groups):
    builder = InlineKeyboardBuilder()
    for group in groups:
        builder.button(
            text=group.name,
            callback_data=group.id,
        )
    return builder.as_markup()
