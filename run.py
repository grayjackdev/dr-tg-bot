from loader import dp, engine, system_settings, jobs
from db import Base, SystemTable
from aiogram import executor, Dispatcher
from utils import BirthdayManager
import asyncio
import aioschedule
import handlers


async def scheduler():
    call_time = system_settings.get("call_time")
    start_interval_survey_func = system_settings.get("start_interval_survey_func")
    check_bd = aioschedule.every(1).day.at(call_time).do(BirthdayManager.check_birthdays)
    check_survey = aioschedule.every(start_interval_survey_func).seconds.do(BirthdayManager.check_survey)
    jobs["check_bd"] = check_bd
    jobs["check_survey"] = check_survey
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
            result = (await conn.execute(SystemTable.__table__.select())).all()

        system_settings["call_time"] = result[0][1]
        system_settings["seconds_survey"] = int(result[0][2])
        system_settings["seconds_survey_2"] = int(result[0][3])
        system_settings["start_interval_survey_func"] = int(result[0][4])

    asyncio.create_task(scheduler())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=init_bot)
