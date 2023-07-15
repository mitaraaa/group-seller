import asyncio
import os

from aiogram import Bot, Dispatcher
from handlers import handlers


async def main():
    dp = Dispatcher()
    dp.include_router(handlers)

    bot = Bot(token=os.getenv("BOT_TOKEN", ""))
    print("Started polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
