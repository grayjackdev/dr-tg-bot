from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from os import environ

load_dotenv()

BOT_TOKEN = environ.get("BOT_TOKEN")

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())




