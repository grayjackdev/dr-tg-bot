from loader import dp, engine
from db import Base
from aiogram import executor, Dispatcher
import handlers


async def init_bot(dp: Dispatcher):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=init_bot)
