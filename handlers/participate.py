from loader import dp, bot
from aiogram.types import CallbackQuery
from keyboards import participate_callback
from loader import async_session
from db import Participant


@dp.callback_query_handler(participate_callback.filter())
async def participate_in_holiday(call: CallbackQuery, callback_data: dict):
    holiday_id = int(callback_data.get("holiday_id"))
    participant = Participant(participant_id=call.from_user.id, holiday_id=holiday_id)
    async with async_session() as session:
        async with session.begin():
            session.add(participant)

    
    await call.message.edit_text("✅Вы записаны в поздравляющие")
