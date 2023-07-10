from loader import dp, async_session, jobs, system_settings
from db import SystemTable, Employee, Holiday, Participant, Wish
from aiogram.types import Message
import aioschedule
from utils import BirthdayManager
from sqlalchemy import select, delete
import datetime


async def change_system_row(column_name, value):
    async with async_session() as session:
        async with session.begin():
            system_row = await session.execute(select(SystemTable))
            system_row = system_row.scalars().one()
            system_row.__setattr__(column_name, value)


@dp.message_handler(commands=['change_time'])
async def change_time(message: Message):
    '''
    Корректировать время запуска функции проверки ближайших ДР(check_birthdays)
    '''
    time = message.get_args().strip()
    try:
        h, m = time.split(":")
        h, m = int(h), int(m)
        datetime.time(hour=h, minute=m)
    except ValueError:
        await message.answer("Неправильный формат времени! Пр-р: 12:56")
        return

    await change_system_row("call_time", time)
    check_bd = jobs.get("check_bd")
    aioschedule.cancel_job(check_bd)
    jobs["check_bd"] = aioschedule.every(1).day.at(time).do(BirthdayManager.check_birthdays)
    system_settings["call_time"] = time
    print("SYSTEM_SETTINGS: ", system_settings)

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

    if emp_id.isdigit():
        emp_id = int(emp_id)
    else:
        await message.answer("ID может быть только числовым!")

    try:
        new_birthday = datetime.datetime.strptime(new_birthday, "%d.%m.%Y").date()
    except ValueError:
        await message.answer("Неверный формат даты!\nПр-р даты: 10.09.2002")
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

    if text:
        await message.answer(text)
    else:
        await message.answer("Пусто!")


@dp.message_handler(commands=["delete_holidays"])
async def show_all(message: Message):
    '''
    Удалить все записи из таблицы holidays
    '''
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Holiday))

    await message.answer('Все праздники удалены!')


@dp.message_handler(commands=["change_sec_survey"])
async def change_sec_survey(message: Message):
    '''
    Функция для изменения кол-во секунд для опроса(по умолчанию 24 часа или 86 400 сек)
    '''

    seconds = message.get_args().strip()

    if seconds.isdigit():
        seconds = int(seconds)
    else:
        await message.answer("Вы должны ввести целое число(кол-во секунд)")
        return

    await change_system_row("seconds_survey", seconds)
    system_settings["seconds_survey"] = seconds
    print("SYSTEM_SETTINGS: ", system_settings)

    await message.answer(f"Кол-во секунд для опроса изменено на {seconds}!")


@dp.message_handler(commands=["change_sec_survey2"])
async def change_sec_survey2(message: Message):
    '''
    Функция для изменения кол-во секунд для опроса, если у нового сотрудника др завтра(по умолчанию 4 часа или 14 400 сек)
    '''

    seconds = message.get_args().strip()

    if seconds.isdigit():
        seconds = int(seconds)
    else:
        await message.answer("Вы должны ввести целое число(кол-во секунд)")
        return

    await change_system_row("seconds_survey_2", seconds)
    system_settings["seconds_survey_2"] = seconds
    print("SYSTEM_SETTINGS: ", system_settings)

    await message.answer(f"Кол-во секунд для опроса в случае если у нового сотрудника завтра ДР изменено на {seconds}!")


@dp.message_handler(commands=["change_isf"])
async def change_isf(message: Message):
    '''
    Функция для изменения интервала запуска функции check_survey
    '''
    seconds = message.get_args().strip()

    if seconds.isdigit():
        seconds = int(seconds)
    else:
        await message.answer("Вы должны ввести целое число(кол-во секунд)")
        return

    await change_system_row("start_interval_survey_func", seconds)
    check_survey = jobs.get("check_survey")
    aioschedule.cancel_job(check_survey)
    jobs["check_survey"] = aioschedule.every(seconds).seconds.do(BirthdayManager.check_survey)
    system_settings["start_interval_survey_func"] = seconds
    print("SYSTEM_SETTINGS: ", system_settings)
    await message.answer(f"Интервал запуска функции проверки окончания опроса изменен на {seconds} секунд")
