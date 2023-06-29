from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
from os import environ

load_dotenv()

BOT_TOKEN = environ.get("BOT_TOKEN")
GROUP_LINK = environ.get("GROUP_LINK")
GROUP_ID = environ.get("GROUP_ID")

PG_USER = environ.get("PG_USER")
PG_PASSWORD = environ.get("PG_PASSWORD")
PG_HOST = environ.get("PG_HOST")
PG_DB = environ.get("PG_DB")


bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())


engine = create_async_engine(
    f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/{PG_DB}",
    echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)







