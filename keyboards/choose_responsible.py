from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

choose_res_callback = CallbackData("choose_res", "holiday_id")


def form_choose_responsible_markup(holiday_id):
    choose_responsible_markup = InlineKeyboardMarkup()
    choose_responsible_markup.add(
        InlineKeyboardButton("Назначить", callback_data=choose_res_callback.new(holiday_id=holiday_id)))
    return choose_responsible_markup
