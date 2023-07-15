from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from emoji import emojize


class Language(str, Enum):
    ru = "ru"
    en = "en"


class LanguageAction(CallbackData, prefix="set_lang"):
    language: Language


def language_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=emojize(":Russia: RU"),
        callback_data=LanguageAction(language=Language.ru),
    )
    builder.button(
        text=emojize(":United_States: EN"),
        callback_data=LanguageAction(language=Language.en),
    )

    return builder.as_markup()
