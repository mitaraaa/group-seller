import os
import asyncio
import logging

from aiogram import Dispatcher
from handlers import handlers
from callbacks import callbacks
from bot import bot

from aiogram.types import BotCommandScopeChat
from aiogram.types.bot_command import BotCommand


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher()
    dp.include_router(handlers)
    dp.include_router(callbacks)
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Start the bot"),
            BotCommand(command="help", description="Show help message"),
            BotCommand(command="language", description="Set language"),
            BotCommand(
                command="groups", description="View all groups available"
            ),
            BotCommand(command="profile", description="View your profile"),
        ],
        language_code="en",
    )
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="help", description="Показать инструкцию"),
            BotCommand(command="language", description="Выбрать язык"),
            BotCommand(
                command="groups",
                description="Просмотреть все доступные группы",
            ),
            BotCommand(command="profile", description="Просмотреть профиль"),
        ],
        language_code="ru",
    )
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Start the bot"),
            BotCommand(command="help", description="Show help message"),
            BotCommand(command="language", description="Set language"),
            BotCommand(
                command="groups", description="View all groups available"
            ),
            BotCommand(command="profile", description="View your profile"),
            BotCommand(
                command="add_group",
                description="Add new group; Args: <steam_link> <price_usd>",
            ),
            BotCommand(
                command="remove_group",
                description="Remove group from view",
            ),
            BotCommand(
                command="add_groups",
                description="Add groups",
            ),
            BotCommand(
                command="lookup",
                description="Check user profile; Args: <username>",
            ),
        ],
        scope=BotCommandScopeChat(chat_id=os.getenv("ADMIN_ID")),
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
