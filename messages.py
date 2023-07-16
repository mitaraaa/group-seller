from aiogram import types
from api.exchange import convert, convert_many
from database import get_group_by_id, get_all_groups
from keyboards import (
    continue_keyboard,
    group_keyboard,
    groups_keyboard,
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

    await context.answer(
        text=language.format_value("choosing_group"),
        reply_markup=groups_keyboard(get_all_groups()),
    )
