from loader import dp, engine, async_session
from sqlalchemy import select
from db import Base, SystemTable
from aiogram import executor, Dispatcher
from utils import BirthdayManager
import asyncio
import aioschedule
import handlers


async def scheduler():
    async with async_session() as session:
        async with session.begin():
            system_row = await session.execute(select(SystemTable))
            system_row = system_row.scalar()
    

    aioschedule.every(1).days.at(system_row.call_time).do(BirthdayManager.check_birthdays)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(3)
 

async def init_bot(dp: Dispatcher):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        result = await conn.execute(SystemTable.__table__.select())
        result = result.all()
        if not result:
            await conn.execute(SystemTable.__table__.insert())
    
    
    asyncio.create_task(scheduler())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=init_bot)
