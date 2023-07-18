from enum import Enum

from aiogram.types import InlineKeyboardButton
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


class GroupAction(CallbackData, prefix="select_payment"):
    group_id: int
    method: str
    price: float


class OrderAction(CallbackData, prefix="payment"):
    group_id: int
    invoice_id: int


class ContinueAction(CallbackData, prefix="continue"):
    pass


class BackAction(CallbackData, prefix="back"):
    action: str
    group_id: int


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


def groups_keyboard(groups: list[Group]):
    builder = InlineKeyboardBuilder()
    buttons = []
    for group in groups:
        buttons.append(
            InlineKeyboardButton(
                text=str(group.name),
                callback_data=GroupsAction(group_id=group.id).pack(),
            )
        )
    builder.row(*buttons, width=1)
    return builder.as_markup()


def group_keyboard(
    language: FluentLocalization, group_id: int, prices: dict[str, float]
):
    builder = InlineKeyboardBuilder()

    if "ru" in language.locales:
        builder.row(
            InlineKeyboardButton(
                text=language.format_value("payment_option_button_rub"),
                callback_data=GroupAction(
                    group_id=group_id, method="RUB", price=prices["RUB"]
                ).pack(),
            )
        )

    buttons = []
    for currency, p in prices.items():
        if currency == "RUB":
            continue

        buttons.append(
            InlineKeyboardButton(
                text=language.format_value(
                    f"payment_option_button_{currency.lower()}"
                ),
                callback_data=GroupAction(
                    group_id=group_id, method=currency, price=p
                ).pack(),
            )
        )
    builder.row(*buttons, width=2)

    builder.row(
        InlineKeyboardButton(
            text=emojize(language.format_value("back")),
            callback_data=BackAction(
                action="groups", group_id=group_id
            ).pack(),
        )
    )

    return builder.as_markup()


def order_keyboard(
    language: FluentLocalization, group_id: int, invoice_id: int, url_pay: str
):
    builder = InlineKeyboardBuilder(
        [
            [
                InlineKeyboardButton(
                    text=emojize(language.format_value("back")),
                    callback_data=BackAction(
                        action="order", group_id=group_id
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=emojize(language.format_value("proceed_button")),
                    url=url_pay,
                ),
            ]
        ]
    )

    return builder.as_markup()
