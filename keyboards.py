from enum import Enum

from aiogram.types import InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from emoji import emojize

from database import get_user_orders, get_group_by_id
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


class GroupRemoveAction(CallbackData, prefix="remove_group"):
    group_id: int


class GroupViewAction(CallbackData, prefix="view_group"):
    group_id: int


class GroupAction(CallbackData, prefix="select_payment"):
    group_id: int
    method: str
    price: float


class ContinueAction(CallbackData, prefix="continue"):
    pass


class BackAction(CallbackData, prefix="back"):
    action: str
    order_id: int


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


def groups_keyboard(groups: list[Group], remove: bool = False):
    builder = InlineKeyboardBuilder()
    buttons = []

    action = GroupRemoveAction if remove else GroupsAction
    for group in groups:
        buttons.append(
            InlineKeyboardButton(
                text=str(group.name),
                callback_data=action(group_id=group.id).pack(),
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
            callback_data=BackAction(action="", order_id=-1).pack(),
        )
    )

    return builder.as_markup()


def order_keyboard(language: FluentLocalization, order_id: int, url_pay: str):
    builder = InlineKeyboardBuilder(
        [
            [
                InlineKeyboardButton(
                    text=emojize(language.format_value("back")),
                    callback_data=BackAction(
                        action="remove_order", order_id=order_id
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


def orders_keyboard(user_id: int):
    builder = InlineKeyboardBuilder()
    orders = get_user_orders(user_id)

    buttons = []
    for order in orders:
        group = get_group_by_id(order.group_id)

        if not group.sold:
            continue

        buttons.append(
            InlineKeyboardButton(
                text=group.name,
                callback_data=GroupViewAction(group_id=group.id).pack(),
            )
        )

    builder.row(*buttons, width=1)

    return builder.as_markup()
