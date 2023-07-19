import asyncio
import os
import logging

from aiogram import Bot, Dispatcher
from handlers import handlers
from callbacks import callbacks


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher()
    dp.include_router(handlers)
    dp.include_router(callbacks)

    bot = Bot(token=os.getenv("BOT_TOKEN", ""), parse_mode="HTML")
    print("Started polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
