from loader import dp, bot, async_session
from aiogram.types import Message, ContentType, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from states import NewEmployee
from db import Employee, Wish
from keyboards import skip_markup, group_link_markup, finish_markup
import datetime


@dp.message_handler(commands=['start'])
async def start_bot(message: Message, state: FSMContext):
    async with async_session() as session:
        async with session.begin():
            user = await session.get(Employee, message.from_user.id)
    
    if not user:
        await NewEmployee.fio.set()
        await message.answer("Введите ваше ФИО")
    else:
        await message.answer("Вы уже добавлены в базу!")


@dp.message_handler(content_types=ContentType.TEXT, state=NewEmployee.fio)
async def get_fio(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await NewEmployee.next()
    await message.answer("Введите вашу дату рождения в формате:\n<i>01.01.1990</i>")


@dp.message_handler(content_types=ContentType.TEXT, state=NewEmployee.birthday)
async def get_birthday(message: Message, state: FSMContext):
    async with state.proxy() as data:
        
        try:
            dt= datetime.datetime.strptime(message.text, "%d.%m.%Y")
        except ValueError:
            await message.answer("Неверный формат! Введите вашу дату рождения в формате:\n<i>01.01.1990</i>")
            return
        
        date = datetime.date(dt.year, dt.month, dt.day)
        data['birthday'] = date
    await NewEmployee.next()
    await message.answer("Добавьте фотографию на которой изображены вы")


@dp.message_handler(content_types=ContentType.PHOTO, state=NewEmployee.photo)
async def get_photo(message: Message, state: FSMContext):
    file_info = await bot.get_file(message.photo[-1].file_id)
    file_ext = file_info.file_path.split(".")[-1]
    path = f"photos/avatars/{message.from_user.id}.{file_ext}"
    await message.photo[-1].download(destination_file=path)
    async with state.proxy() as data:
        data['photo_path'] = path

    await NewEmployee.next()
    await message.answer("Введите пожелание к подарку или пропустите данный пункт", reply_markup=skip_markup)


@dp.message_handler(content_types=ContentType.TEXT, state=NewEmployee.wish_list)
async def get_wish(message: Message, state: FSMContext):
    
    if message.text == "Пропустить":
        async with state.proxy() as data:
            data["wishes"] = []
    elif message.text != "Завершить":    
        async with state.proxy() as data:
            if data.get("wishes") is None:
                data["wishes"] = list()
            data["wishes"].append(Wish(text=message.text))
            await message.answer("Введите еще одно пожелание или завершите данный пункт", reply_markup=finish_markup)
        return
    
    await NewEmployee.next()
    await message.answer("И последнее. Добавьте свои Банковские реквизиты, номер карты и банк получателя", reply_markup=ReplyKeyboardRemove())





@dp.message_handler(content_types=ContentType.TEXT, state=NewEmployee.details)
async def get_details(message: Message, state: FSMContext):
    
    state_data = await state.get_data()
    details = message.text
    name = state_data.get("name")
    birthday = state_data.get("birthday")
    photo_path = state_data.get("photo_path")
    wishes = state_data.get("wishes")

    async with async_session() as session:
        async with session.begin():
            emp = Employee(id=message.from_user.id, fio=name, birthday=birthday, photo=photo_path, details=details)
            emp.wishes.extend(wishes)
            session.add(emp)
    

    await state.reset_state()
    await message.answer("Поздравляю! Вы успешно добавлены в ряды именинников")
    await message.answer("Вот ссылка на чат поздравлений", reply_markup=group_link_markup)




