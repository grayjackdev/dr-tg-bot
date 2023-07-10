from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

participate_callback = CallbackData("participate", "holiday_id")


def form_survey_markup(holiday_id):
    survey_markup = InlineKeyboardMarkup()
    survey_markup.add(InlineKeyboardButton("+", callback_data=participate_callback.new(holiday_id=holiday_id)))
    return survey_markup
