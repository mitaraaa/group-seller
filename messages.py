from asyncio import sleep
from datetime import timedelta, datetime
import os
from math import ceil
from aiogram import types
from api.exchange import convert, convert_many
from api.payment import Invoice, check_status, create_invoice
from database import (
    get_group_by_id,
    get_all_groups,
    create_order,
    get_order,
    set_sold,
    remove_order,
)
from database.models import Group, Order
from keyboards import (
    GroupAction,
    continue_keyboard,
    group_keyboard,
    groups_keyboard,
    order_keyboard,
)
from locales import get_user_language
from bot import bot


async def send_group_message(callback: types.CallbackQuery, group_id: int):
    language = get_user_language(callback.from_user.id)
    group = get_group_by_id(group_id)

    prices = convert_many(price=group.price)
    price = (
        f"{convert(group.price, 'RUB'):.2f} RUB"
        if "ru" in language.locales
        else f"{group.price:.2f} USD"
    )

    text = []
    if "ru" in language.locales:
        rub = prices["RUB"]
        text.append(
            language.format_value(
                "payment_option_rub", {"price": f"{rub:.2f} RUB"}
            )
        )

    for currency, p in prices.items():
        if currency == "RUB":
            continue

        text.append(
            language.format_value(
                f"payment_option_{currency.lower()}",
                {"price": f"{p} {currency} ({price})"},
            )
        )

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
    )
    await callback.message.answer(
        "\n".join(text),
        reply_markup=group_keyboard(language, group_id, prices),
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
        disable_web_page_preview=True,
    )


async def send_groups_message(
    context: types.CallbackQuery | types.Message, from_continue: bool = False
):
    language = get_user_language(context.from_user.id)

    if from_continue:
        if isinstance(context, types.Message):
            await context.delete()
        else:
            await context.message.delete()

    context = (
        context if isinstance(context, types.Message) else context.message
    )
    keyboard = groups_keyboard(get_all_groups())
    if len(keyboard.inline_keyboard) == 0:
        await context.answer(text=language.format_value("empty_list_of_group"))
    else:
        await context.answer(
            text=language.format_value("choosing_group"),
            reply_markup=(keyboard),
        )


def calculate_time(order: Order):
    until = order.date + timedelta(
        hours=int(os.getenv("TZ_OFFSET")),
        minutes=int(os.getenv("TIME_TO_PAY")),
    )

    now = datetime.utcnow() + timedelta(
        hours=int(os.getenv("TZ_OFFSET")),
    )

    left = until - now

    return until, left


async def send_order_message(
    callback: types.CallbackQuery,
    callback_data: GroupAction,
):
    language = get_user_language(callback.from_user.id)

    order_id = create_order(
        callback.from_user.id,
        callback_data.group_id,
        callback_data.method,
        callback_data.price,
    )
    group = get_group_by_id(callback_data.group_id)
    order = get_order(order_id)

    datetime_until, datetime_left = calculate_time(order)

    time_until = (
        datetime_until.time().isoformat()[:5]
        + f" ({int(os.getenv('TZ_OFFSET')):+d} UTC)"
    )

    invoice = create_invoice(
        callback_data.method,
        callback_data.price,
    )

    await callback.message.edit_text(
        language.format_value(
            "order",
            {
                "name": group.name,
                "price": f"{callback_data.price} {callback_data.method}",
                "order_id": order_id,
                "payment_option": language.format_value(
                    f"payment_option_button_{callback_data.method.lower()}"
                ),
                "time_remaining": ceil(datetime_left.total_seconds() / 60),
                "time_until": time_until,
            },
        ),
        reply_markup=order_keyboard(language, order.id, invoice.pay_url),
    )
    await check_payment(callback, callback_data, invoice, group, order)


async def check_payment(
    callback: types.CallbackQuery,
    callback_data,
    invoice: Invoice,
    group: Group,
    order: Order,
):
    language = get_user_language(callback.from_user.id)

    time_passed = 0
    while ((status := check_status(invoice.id)) != "paid") and (
        time_passed < int(os.getenv("TIME_TO_PAY")) * 60
    ):
        await sleep(5)
        time_passed += 5

        group = get_group_by_id(group.id)
        if group.sold:
            status = "expired"
            break

        order = get_order(order.id)
        if not order:
            status = "expired"
            break

        if time_passed % 60 == 0:
            datetime_until, datetime_left = calculate_time(order)

            time_until = (
                datetime_until.time().isoformat()[:5]
                + f" ({int(os.getenv('TZ_OFFSET')):+d} UTC)"
            )

            await callback.message.edit_text(
                language.format_value(
                    "order",
                    {
                        "name": group.name,
                        "price": f"{callback_data.price} {callback_data.method}",
                        "order_id": order.id,
                        "payment_option": language.format_value(
                            f"payment_option_button_{callback_data.method.lower()}"
                        ),
                        "time_remaining": ceil(
                            datetime_left.total_seconds() / 60
                        ),
                        "time_until": time_until,
                    },
                ),
                reply_markup=order_keyboard(
                    language, order.id, invoice.pay_url
                ),
            )

    if status == "paid":
        set_sold(group.id)
        await callback.message.edit_text(
            language.format_value(
                "order_success",
                {
                    "name": group.name,
                    "order_id": order.id,
                },
            ),
        )
        await bot.send_message(
            os.getenv("CHANNEL_ID"),
            language.format_value(
                "channel_sold",
                {
                    "link": f"https://steamcommunity.com/groups/{group.url}",
                    "name": group.name,
                },
            ),
            disable_web_page_preview=True,
        )
        await callback.answer()
    else:
        remove_order(order.id)
        await callback.answer()
        await callback.message.edit_text(
            language.format_value("order_expired")
        )
