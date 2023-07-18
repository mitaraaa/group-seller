from datetime import datetime, timedelta
import time
from aiogram import types
from aiogram.fsm.context import FSMContext
from api.exchange import convert, convert_many
from api.payment import check_status, create_invoice
from database import (
    get_group_by_id,
    get_all_groups,
    create_order,
    get_order,
    set_sold,
)
from fsm import GroupStates
from keyboards import (
    GroupAction,
    continue_keyboard,
    group_keyboard,
    groups_keyboard,
    order_keyboard,
)
from locales import get_user_language


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
        parse_mode="HTML",
    )
    await callback.message.answer(
        "\n".join(text),
        parse_mode="HTML",
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
        parse_mode="HTML",
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


async def send_order_message(
    callback: types.CallbackQuery,
    callback_data: GroupAction,
    state: FSMContext,
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

    datetime_until = order.date + timedelta(minutes=15)
    time_until = datetime_until.time()

    invoice = create_invoice(
        callback_data.method,
        callback_data.price,
        (datetime_until - datetime(1970, 1, 1)).total_seconds(),
        group.id,
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
                "time_remaining": 15,
                "time_until": f"{(time_until.hour + 3) % 24:02}"
                ":"
                f"{time_until.second:02}",  # tz hack
            },
        ),
        parse_mode="HTML",
        reply_markup=order_keyboard(
            language, callback_data.group_id, invoice.id, invoice.pay_url
        ),
    )
    await state.set_state(GroupStates.order)
    await check_payment(callback, invoice.id, group.id, group.name, order_id, state)


async def check_payment(
    callback: types.CallbackQuery,
    invoice_id: int,
    group_id: int,
    group_name: str,
    order_id: int,
    state: FSMContext,
):
    language = get_user_language(callback.from_user.id)

    while not check_status(invoice_id):
        time.sleep(5)

    set_sold(group_id)
    await callback.message.edit_text(
        language.format_value(
            "order_success",
            {
                "name": group_name,
                "order_id": order_id,
            }
            ),
        parse_mode="HTML",
    )
    await state.clear()
    await callback.answer()
