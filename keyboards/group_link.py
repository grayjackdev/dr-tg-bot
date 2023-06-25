from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loader import GROUP_LINK

group_link_markup = InlineKeyboardMarkup()
group_link_markup.add(InlineKeyboardButton("Чат", GROUP_LINK))
