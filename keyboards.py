from aiogram.types.inline_keyboard import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.callback_data import CallbackData
from emoji import emojize

language_callback = CallbackData("language", "language")

LANGUAGE_KEYBOARD = InlineKeyboardMarkup().add(
    InlineKeyboardButton(
        emojize(":Russia: RU"),
        callback_data=language_callback.new(language="RU"),
    ),
    InlineKeyboardButton(
        emojize(":United_States: EN"),
        callback_data=language_callback.new(language="EN"),
    ),
)
