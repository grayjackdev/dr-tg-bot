from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

skip_markup = ReplyKeyboardMarkup(resize_keyboard=True)
skip_markup.add(KeyboardButton("Пропустить"))

finish_markup = ReplyKeyboardMarkup(resize_keyboard=True)
finish_markup.add(KeyboardButton("Завершить"))