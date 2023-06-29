from db import Employee, Holiday, StatusHoliday
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from loader import async_session, bot, GROUP_ID
from keyboards import form_survey_markup
import datetime

class BirthdayManager:
    
    @classmethod
    async def notify_all_about_birthday(cls, emp: Employee, holiday_id, days_before, employees):
        markup = form_survey_markup(holiday_id)
        emp_url = f'tg://user?id={emp.id}'
        emp_html = f"<a href=\"{emp_url}\">{emp.fio}</a>"
        for i in employees:
            if i.id == emp.id:
                continue
            await bot.send_message(i.id, f"У {emp_html} через {days_before} дней день рождения!"
                                   " Нажми на + если хочешь скинуться на подарок",
                                   reply_markup=markup) 


    @classmethod
    async def check_birthdays(cls):
        async with async_session() as session:
            async with session.begin():
                employees = await session.execute(select(Employee).options(selectinload(Employee.holidays_bb)))
                employees = employees.scalars().all()

        for emp in employees:
            current_date = datetime.date.today()
            birthday_in_this_year = datetime.date(current_date.year, emp.birthday.month, emp.birthday.day)
            difference = birthday_in_this_year - current_date
            
            if difference <= datetime.timedelta(days=7) and ((not emp.holidays_bb) or emp.holidays_bb[0].status == StatusHoliday.complete):

                hd = Holiday(birthday_boy_id=emp.id, holiday_date=birthday_in_this_year)
                async with async_session() as session:
                    async with session.begin():
                        session.add(hd)
                
                
                await bot.ban_chat_member(GROUP_ID, emp.id)
                await cls.notify_all_about_birthday(emp, hd.id, difference.days, employees)