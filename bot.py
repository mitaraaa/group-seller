import os
from aiogram import Bot


bot = Bot(token=os.getenv("BOT_TOKEN", ""), parse_mode="HTML")
