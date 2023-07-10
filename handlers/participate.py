from loader import dp, bot
from aiogram.types import CallbackQuery
from keyboards import participate_callback
from loader import async_session
from db import Participant, Holiday, StatusHoliday


@dp.callback_query_handler(participate_callback.filter())
async def participate_in_holiday(call: CallbackQuery, callback_data: dict):
    holiday_id = int(callback_data.get("holiday_id"))
    async with async_session() as session:
        async with session.begin():
            holiday = await session.get(Holiday, holiday_id)
            if holiday:
                if holiday.status == StatusHoliday.waiting:
                    participant = Participant(participant_id=call.from_user.id, holiday_id=holiday_id)
                    session.add(participant)
                else:
                    await call.message.delete()
                    await call.message.answer("Для данного праздника список уже был сформирован!")
                    return
            else:
                await call.message.delete()
                await call.message.answer("Праздник не найден!")
                return

    await call.message.delete()
    await call.message.answer("✅Вы записаны в поздравляющие")
