from aiogram.dispatcher.filters.state import State, StatesGroup


class ChooseResponsible(StatesGroup):
    number = State()
    gift_amount = State()
