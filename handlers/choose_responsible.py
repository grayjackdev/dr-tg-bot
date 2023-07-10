from aiogram.dispatcher import FSMContext
from loader import dp, async_session
from aiogram.types import Message, CallbackQuery, ContentType
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from states import ChooseResponsible
from keyboards import choose_res_callback
from db import Holiday, StatusHoliday
from utils import Tools, BirthdayManager


@dp.callback_query_handler(choose_res_callback.filter())
async def enter_number_responsible(call: CallbackQuery, state: FSMContext, callback_data: dict):
    holiday_id = int(callback_data.get("holiday_id"))

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Holiday).where(Holiday.id == holiday_id).options(selectinload(Holiday.participants),
                                                                        selectinload(Holiday.birthday_boy),
                                                                        selectinload(Holiday.responsible)
                                                                        )
            )
            holiday = result.scalars().one()

            if holiday:
                if holiday.status == StatusHoliday.ready_list:
                    await state.update_data(holiday=holiday)
                    await ChooseResponsible.number.set()
                    await call.message.answer("Введите номер из списка того, кто будет ответственным")
                    await call.answer()
                    await call.message.edit_reply_markup()
                else:
                    await call.message.edit_text("Праздник уже завершен!")
                    return
            else:
                await call.message.edit_text("Праздник не найден!")
                return


@dp.message_handler(content_types=ContentType.TEXT, state=ChooseResponsible.number)
async def enter_gift_amount(message: Message, state: FSMContext):
    try:
        int(message.text)
    except ValueError:
        await message.answer("Номер должен быть числом! Повторите попытку")
        return

    number = int(message.text)
    state_data = await state.get_data()
    holiday = state_data.get("holiday")
    participants = holiday.participants
    if number < 1 or number > len(participants):
        await message.answer("Размер списка меньше или больше, чем введенное вами число! Повторите попытку")
        return
    else:
        participant = participants[number - 1]
        holiday.responsible = participant.employee
        await state.update_data(holiday=holiday)
        await ChooseResponsible.next()
        await message.answer(
            f"Хорошо! Вы назначали {Tools.create_link_to_emp(participant.employee)} ответственным. Теперь введите сумму подарка")


@dp.message_handler(content_types=ContentType.TEXT, state=ChooseResponsible.gift_amount)
async def save_data_about_responsible(message: Message, state: FSMContext):

    try:
        int(message.text)
    except ValueError:
        await message.answer("Сумма должна быть числом! Повторите попытку")
        return

    gift_amount = int(message.text)
    state_data = await state.get_data()
    holiday = state_data.get("holiday")
    holiday.gift_amount = gift_amount

    async with async_session() as session:
        async with session.begin():
            session.add(holiday)

    await state.finish()
    await message.answer("Данные сохранены!")
    await BirthdayManager.notify_all_participants_about_res(holiday)
