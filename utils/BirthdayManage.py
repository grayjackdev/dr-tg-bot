import asyncio
from aiogram.types import InputFile
from db import Employee, Holiday, StatusHoliday, Wish
from . import Tools
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from loader import async_session, bot, GROUP_ID, system_settings, OFFICE_MANAGER_ID
from keyboards import form_survey_markup, form_choose_responsible_markup, group_link_markup
import datetime


class BirthdayManager:

    @classmethod
    async def notify_all_about_birthday(cls, emp: Employee, days_before, employees, holiday_id=None):
        emp_html = Tools.create_link_to_emp(emp)
        if holiday_id:
            markup = form_survey_markup(holiday_id)
            text = f"У {emp_html} через {days_before} дней день рождения! Нажми на + если хочешь скинуться на подарок"
        else:
            markup = None
            text = f"У {emp_html} через {days_before} дня день рождения!"
        for i in employees:
            if i.id == emp.id:
                continue
            photo = InputFile(emp.photo)
            await bot.send_photo(i.id, photo, text, reply_markup=markup)
            await asyncio.sleep(0.25)

    @classmethod
    async def check_birthdays(cls):
        async with async_session() as session:
            async with session.begin():
                employees = await session.execute(select(Employee).options(selectinload(Employee.holidays_bb)))
                employees = employees.scalars().all()

        for emp in employees:
            current_date = datetime.date.today()
            bd_in_current_year = datetime.date(current_date.year, emp.birthday.month, emp.birthday.day)

            if bd_in_current_year >= current_date:
                next_birthday = bd_in_current_year
            else:
                next_birthday = datetime.date(current_date.year + 1, emp.birthday.month, emp.birthday.day)

            difference = next_birthday - current_date

            if difference <= datetime.timedelta(days=7) \
                    and ((not emp.holidays_bb) or emp.holidays_bb[0].status == StatusHoliday.complete):

                hd = Holiday(birthday_boy_id=emp.id, holiday_date=next_birthday)
                async with async_session() as session:
                    async with session.begin():
                        session.add(hd)

                await bot.ban_chat_member(GROUP_ID, emp.id)
                await cls.notify_all_about_birthday(emp, difference.days, employees, hd.id)


            elif difference == datetime.timedelta(days=3) and (emp.holidays_bb[0].status == StatusHoliday.ready_list):
                await cls.notify_all_about_birthday(emp, difference.days, employees)


            elif difference == datetime.timedelta(days=0) and (emp.holidays_bb[0].status == StatusHoliday.ready_list):
                text_for_group = f'Сегодня у {Tools.create_link_to_emp(emp)} день рождения!'
                await bot.send_message(GROUP_ID, text_for_group)

                text_for_bb = f'Здравствуйте, {emp.fio} ! С днем рождения! Заходи в чат, чтобы мы могли тебя поздравить!'

                await bot.unban_chat_member(GROUP_ID, emp.id)
                await bot.send_message(emp.id, text_for_bb, reply_markup=group_link_markup)

                holiday = emp.holidays_bb[0]
                holiday.status = StatusHoliday.complete

                async with async_session() as session:
                    async with session.begin():
                        session.add(holiday)

    @classmethod
    async def survey_end(cls, holiday: Holiday):
        async with async_session() as session:
            async with session.begin():
                wishes_birthday_boy = await session.execute(
                    select(Wish).where(Wish.employee_id == holiday.birthday_boy_id))
                wishes_birthday_boy = wishes_birthday_boy.scalars().all()
                holiday.status = StatusHoliday.ready_list
                session.add(holiday)



        emp_html = Tools.create_link_to_emp(holiday.birthday_boy)

        if holiday.participants:

            text_for_manager = f"Привет! Список желающих поздравить {emp_html} сформирован:\n\n"
            text_for_group = f"Список желающих поздравить {emp_html} сформирован:\n\n"

            result = Tools.form_list_participants(holiday.participants)
            text_for_manager += result[0]
            text_for_group += result[0]

            await bot.send_message(OFFICE_MANAGER_ID, text_for_manager)
            await bot.send_message(GROUP_ID, text_for_group)

            index = result[1]
            while index is not None:
                result = Tools.form_list_participants(holiday.participants, index)
                text = f"Желающие поздравить {emp_html}:\n\n" + result[0]
                await bot.send_message(OFFICE_MANAGER_ID, text)
                await bot.send_message(GROUP_ID, text)
                index = result[1]

            manager_markup = form_choose_responsible_markup(holiday.id)
            await bot.send_message(OFFICE_MANAGER_ID, f"Назначьте ответственного за покупку подарка для {emp_html}",
                                   reply_markup=manager_markup)

            if wishes_birthday_boy:
                title_list_wishes = f"Список пожеланий {emp_html}:\n\n"
                result = Tools.form_list_wishes(wishes_birthday_boy)
                text_wishes = title_list_wishes + result[0]
                await bot.send_message(GROUP_ID, text_wishes)
                index = result[1]
                while index is not None:
                    result = Tools.form_list_wishes(wishes_birthday_boy, index)
                    text_wishes = title_list_wishes + result[0]
                    await bot.send_message(GROUP_ID, text_wishes)
                    index = result[1]

        else:
            text = f"Никто не захотел скидываться на подарок для {emp_html}"
            await bot.send_message(GROUP_ID, text)

    @classmethod
    async def check_survey(cls):
        async with async_session() as session:
            async with session.begin():
                holidays = await session.execute(select(Holiday).where(Holiday.status == StatusHoliday.waiting).options(
                    selectinload(Holiday.birthday_boy), selectinload(Holiday.participants)))
                holidays = holidays.scalars().all()

        for hd in holidays:
            days_before_bd = hd.holiday_date - datetime.date.today()
            time_after_create_holiday = datetime.datetime.now() - hd.record_time
            seconds_survey = system_settings["seconds_survey"]
            seconds_survey_2 = system_settings["seconds_survey_2"]

            if days_before_bd == datetime.timedelta(days=1) and \
                    time_after_create_holiday >= datetime.timedelta(seconds=seconds_survey_2):
                await cls.survey_end(hd)

            elif days_before_bd > datetime.timedelta(days=1) and \
                    time_after_create_holiday >= datetime.timedelta(seconds=seconds_survey):
                await cls.survey_end(hd)

    @staticmethod
    async def notify_all_participants_about_res(holiday):
        details = holiday.responsible.details
        gift_amount = holiday.gift_amount
        sum_for_each = int(gift_amount / len(holiday.participants))
        for p in holiday.participants:
            if p.participant_id == holiday.responsible_id and p.participant_id > 100:
                text = f'''
Вас назначали ответственным за покупку подарка для {Tools.create_link_to_emp(holiday.birthday_boy)}. Сумма подарка: {gift_amount} руб
                '''
                await bot.send_message(p.participant_id, text)
            else:
                text = f'''
{Tools.create_link_to_emp(holiday.responsible)} назначен ответственным за 
покупку подарка для {Tools.create_link_to_emp(holiday.birthday_boy)}

Переведите {sum_for_each} руб на:

{details}
                    '''

                await bot.send_message(p.participant_id, text)
