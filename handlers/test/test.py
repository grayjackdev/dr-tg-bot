from loader import dp, async_session
from db import SystemTable, Employee, Holiday
from aiogram.types import Message
import aioschedule
from utils import BirthdayManager
from sqlalchemy import select, delete
import datetime


@dp.message_handler(commands=['change_time'])
async def change_time(message: Message):
    '''
    Корректировать время запуска функции проверки ближайших ДР(check_birthdays)
    '''
    time = message.get_args().strip()
    async with async_session() as session:
        async with session.begin():
            system_row = await session.get(SystemTable, 1)
            system_row.call_time = time

    aioschedule.clear()
    aioschedule.every(1).days.at(time).do(BirthdayManager.check_birthdays)

    await message.answer(f"Теперь проверка ближайших ДР будет каждый день в {time}")
    

@dp.message_handler(commands=['change_birthday'])
async def change_birthday(message: Message):
    '''
    Функция для изменения ДР сотрудника
    '''
    args = message.get_args().strip().split()
    if len(args) > 2:
        await message.answer("Данная команда принимает всего 2 аргумента!")
        return
    
    emp_id, new_birthday = args

    try:
        new_birthday = datetime.datetime.strptime(new_birthday, "%d.%m.%Y").date()
        emp_id = int(emp_id)
    except ValueError:
        await message.answer("Неверный формат даты или ID!\n\nПр-р даты: 10.09.2002\n\nПр-р ID: 3434331")
        return

    
    async with async_session() as session:
        async with session.begin():
            emp = await session.get(Employee, emp_id)
            if emp:
                emp.birthday = new_birthday
            else:
                await message.answer("Нет сотрудника с таким ID")
                return

    await message.answer(f"Дата рождения <i>{emp.fio}</i> изменена на <i>{new_birthday}</i>")


@dp.message_handler(commands=["show_all"])
async def show_all(message: Message):
    '''
    Функция вывода всех сотрудников в формате ID:ФИО
    '''
    async with async_session() as session:
        async with session.begin():
            employees = await session.execute(select(Employee))
            employees = employees.scalars()

    text = ""
    for emp in employees:
        text += f"<code>{emp.id}</code>:\n{emp.fio}\n\n"
    
    await message.answer(text)

@dp.message_handler(commands=["delete_holidays"])
async def show_all(message: Message):
    '''
    Удалить все записи из таблицы holidays
    '''
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Holiday))

    await message.answer('Все праздники удалены!')



