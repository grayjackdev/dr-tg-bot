from aiogram.dispatcher.filters.state import State, StatesGroup

class NewEmployee(StatesGroup):
    fio = State() 
    birthday = State() 
    photo = State() 
    wish_list = State()
    details = State()


