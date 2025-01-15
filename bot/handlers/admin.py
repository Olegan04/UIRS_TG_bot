from aiogram import Bot, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from bot.db.requests import get_user_by_id, new_service, get_service_by_id, get_idService
from bot.db.requests import get_bike_by_id, get_idBike, new_bike, list_bron, delete_uslug, delete_bike
from bot.db.requests import get_id_all_users, get_id_users
from bot.db.models import Users, Services, Reservation, Bikes
from bot.handlers.states import Admin

import textwrap
import logging

logging.basicConfig(level=logging.INFO)

router = Router(name="Admin")

vozm = ["Посмотреть бронь", "Написать пользователям",
        "Изменить информацию об услуге", "Добавить новую услугу", "Удалить услугу", 
        "Изменить информацию об велосипеде", "Добавить велосипед", "Удалить велосипед",
        "Редактировать информацию", "Удалить запись"]

def make_row_keyboard(items: list[str], kol_bt: int = 2) -> ReplyKeyboardMarkup:
    keyboard = [items[i:i + kol_bt] for i in range (0, len(items), kol_bt)]
    keyboard = [[KeyboardButton(text=item) for item in row] for row in keyboard]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(Command("Iadmin"))
async def prAdmin(message: Message, state: FSMContext, session: AsyncSession):
    user = await get_user_by_id(session, message.from_user.id)
    if (user.status == "admin"):
        await message.answer(
            "Введите пароль",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Admin.login)
    
@router.message(Admin.login)
async def password(message: Message, state: FSMContext):
    if(message.text.lower() == "1234.,fgh"):
        await message.answer(
            "Добро пожаловать",
            reply_markup=make_row_keyboard(vozm)
        )
        await state.set_state(Admin.work)
    else:
        await message.answer("Неверный пароль")

@router.message(Admin.work, F.text == vozm[3])
async def updata(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        "Введите через ; id услуги, название услуги, ее продолжительность, цену и местонахождения (Шерегеш, Белокуриха)",
        reply_markup=ReplyKeyboardRemove()        
    )
    await state.set_state(Admin.new_uslug)

@router.message(Admin.new_uslug)
async def newData(message: Message, state: FSMContext, session: AsyncSession):
    s = message.text
    data = s.split(';')
    if(len(data) == 5):
        inf = await new_service(session, int(data[0]), data[1], data[2], int(data[3]), data[4])
        if (inf == 101):
            await message.answer("Данный id уже занят")
        else:
            await message.answer(
                "Услуга добавлена",
                reply_markup=make_row_keyboard(vozm)
            )
            await state.set_state(Admin.work)
    else:
        await message.answer("Некоректный ввод")

@router.message(Admin.work, F.text == vozm[2])
async def corectUslug(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        "Если знаете id услуги введите его\nЕсли нет, то укажите название, продолжительность и место через ;",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Admin.corect_uslug)

@router.message(Admin.corect_uslug)
async def corectData(message: Message, state: FSMContext, session: AsyncSession):
    s = message.text
    data = s.split(';')
    service: Services
    if len(data) == 1:
        service = await get_service_by_id(session, int(data[0]))
    elif len(data) == 3:
        it = await get_idService(session, data[0], data[1], data[2])
        service = await get_service_by_id(session, it)
    else:
        service = None
        await message.answer("Проверьте коректность данных и повторите попытку")
    
    if service is not None:
        await state.update_data(serviceId = service.idservice)
        await message.answer(f"""Данные услуги:\nНазвание: {service.nameService}\nПродолжительность: {service.duration}\nЦена: {service.price}\nМесто: {service.location}""")
        await message.answer(textwrap.dedent("Введите через ;\n1 - если хотите изменить название\n2 - если хотите изменить продолжительность\n3 - если хотите изменить цену\n4 - если хотите изменить место\nЗатем также через ; введите новые данные\nНапример: 2;3;спуск;1000"))
        await state.set_state(Admin.save_change_uslug)

@router.message(Admin.save_change_uslug)
async def saveChangeUslug(message: Message, state: FSMContext, session: AsyncSession):
    s = message.text
    data = s.split(';')
    if len(data) % 2 != 0:
        await message.answer("Проверьте коректность ввода и повторите попытку")
    else:
        d = await state.get_data()
        await state.clear()
        service = await get_service_by_id(session, d["serviceId"])
        x = int(len(data) / 2)
        for i in range(x):
            if data[i] == '1':
                service.nameService = data[x+i]
            elif data[i] == '2':
                service.duration = data[x+i]
            elif data[i] == '3':
                service.price = int(data[x+i])
            elif data[i] == '4':
                service.location = data[x+i]
        await session.commit()
        await message.answer(
            "Данные успешно обновленны",
            reply_markup=make_row_keyboard(vozm)
        )
        await state.set_state(Admin.work)
        
@router.message(Admin.work, F.text == vozm[5])
async def corectBike(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        "Если знаете id велосипеда введите его\nЕсли нет, то укажите его название",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Admin.corect_bike)

@router.message(Admin.corect_bike)
async def updataBike(message: Message, state: FSMContext, session: AsyncSession):
    s = message.text
    id_bike: int
    if (s.isdigit()):
        id_bike = int(s)
    else:
        id_bike = await get_idBike(session, s)
    bike = await get_bike_by_id(session, id_bike)

    if bike is None:
        await message.answer("Велосипед не найдена, проверьте коректность ввода и повторите попытку")
    else:
        await state.update_data(bikeId = bike.id_bike)
        await message.answer(f"""Информация о велосипеде:\nНазвание: {bike.name}""")
        await message.answer(textwrap.dedent("""Введите новое название велосипеда"""))
        await state.set_state(Admin.save_change_bike)

@router.message(Admin.save_change_bike)
async def saveChangeBike(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await state.clear()
    bike = await get_bike_by_id(session, data["bikeId"])
    bike.name = message.text
    await session.commit()
    await message.answer(
        "Данные успешно обновленны",
        reply_markup=make_row_keyboard(vozm)
    )
    await state.set_state(Admin.work)

@router.message(Admin.work, F.text == vozm[6])
async def newBike(message: Message, state: FSMContext):
    await message.answer(
        "Введите через ; id велосипеда и название велосипеда",
        reply_markup=ReplyKeyboardRemove()        
    )
    await state.set_state(Admin.new_bike)

@router.message(Admin.new_bike)
async def newData(message: Message, state: FSMContext, session: AsyncSession):
    s = message.text
    data = s.split(';')
    if(len(data) == 2):
        inf = await new_bike(session, int(data[0]), data[1])
        if (inf == 101):
            await message.answer("Данный id уже занят")
        else:
            await message.answer(
                "Услуга добавлена",
                reply_markup=make_row_keyboard(vozm)
            )
            await state.set_state(Admin.work)
    else:
        await message.answer("Некоректный ввод")
 

@router.message(Admin.work, F.text == vozm[0])
async def date_bron(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        "Введите байк-парк (Шерегеш или Белокуриха), и день, месяц (числом) и год (если хотите посмотреть бронь на конкретную дату, иначе выведится бронь на ближащую неделю) через пробел",
        reply_markup=ReplyKeyboardRemove()        
    )
    await state.set_state(Admin.bron_date)

@router.message(Admin.bron_date)
async def bron_on_data(message: Message, state: FSMContext, session: AssertionError):
    d = message.text.split(' ')
    if len(d) == 4:
        date = datetime(int(d[3]), int(d[2]), int(d[1]))
        bron = await list_bron(session, date, d[0])
        s = ""
        if len(bron) != 0: 
            s = f"Бронь на {date.strftime('%Y-%m-%d')}:\n"
            for j in bron:
                if j.nameBike is not None:
                    s+=f"Имя: {j.name}, фамилия: {j.famaly}, номер: {j.namber}, услуга: {j.nameService} {j.nameBike} {j.duration}, время {j.time.strftime('%H:%M')}\n"
                else:
                    s+=f"Имя: {j.name}, фамилия: {j.famaly}, номер: {j.namber}, услуга: {j.nameService} {j.duration}, время: {j.time.strftime('%H:%M')}\n"
        else:
            s = f"Брони на {date.strftime('%Y-%m-%d')} нет"
        await message.answer(s, reply_markup=make_row_keyboard(vozm))

    elif len(d) == 1:
        await message.answer("Ниже представлена запись на ближайшую неделю")
        date = datetime.now()
        day = date.day
        month = date.month
        year = date.year
        for i in range(day, day+7):
            date_now = datetime(year, month, i)
            bron = await list_bron(session, date_now, d[0])
            s = ""
            if len(bron) != 0:
                s = f"Бронь на {date_now.strftime('%Y-%m-%d')}:\n"
                for j in bron:
                    if j.nameBike is not None:
                        s+=f"Имя: {j.name}, фамилия: {j.famaly}, номер: {j.namber}, услуга: {j.nameService} {j.nameBike} {j.duration}, время {j.time.strftime('%H:%M')}\n"
                    else:
                        s+=f"Имя: {j.name}, фамилия: {j.famaly}, номер: {j.namber}, услуга: {j.nameService} {j.duration}, время: {j.time.strftime('%H:%M')}\n"
            else:
                s = f"Брони на {date_now.strftime('%Y-%m-%d')} нет"
            if i < day + 6:
                await message.answer(s)
            else:
                await message.answer(s, reply_markup=make_row_keyboard(vozm))
    await state.set_state(Admin.work)

@router.message(Admin.work, F.text == vozm[4])
async def choice_del_uslug(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        "Если знаете id услуги введите его\nЕсли нет, то укажите название, продолжительность и место через ;",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Admin.del_uslug)

@router.message(Admin.del_uslug)
async def del_uslug(message: Message, state: FSMContext, session: AsyncSession):
    s = message.text
    data = s.split(';')
    service: Services
    id: int
    if len(data) == 1:
        id = int(data[0])
    elif len(data) == 3:
        id = await get_idService(session, data[0], data[1], data[2]) 
    else:
        id = -1
        await message.answer("Проверьте коректность данных и повторите попытку")

    if id != -1:
        await delete_uslug(session, id)
    
    await message.answer(
        "Услуга удалена",
        reply_markup=make_row_keyboard(vozm)
    )
    await state.set_state(Admin.work)
        
@router.message(Admin.work, F.text == vozm[7])
async def choice_del_bike(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        "Если знаете id велосипеда введите его\nЕсли нет, то укажите его название",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Admin.del_bike)

@router.message(Admin.del_bike)
async def del_bike(message: Message, state: FSMContext, session: AsyncSession):
    s = message.text
    id_bike: int
    if (s.isdigit()):
        id_bike = int(s)
    else:
        id_bike = await get_idBike(session, s)
    bike = await get_bike_by_id(session, id_bike)

    if bike is None:
        await message.answer("Велосипед не найдена, проверьте коректность ввода и повторите попытку")
    else:
        await delete_bike(session, id_bike)

    await message.answer(
        "Велосипед удален",
        reply_markup=make_row_keyboard(vozm)
    )
    await state.set_state(Admin.work)

@router.message(Admin.work, F.text == vozm[1])
async def start_sms(messege: Message, state: FSMContext, session: AsyncSession):
    await messege.answer(
        "Введите:\n- 1, если хотите написать всем пользователям\n- 2 и локацию через пробел, если хотите нарисать тем кто пользуется услугами конкретного байк-парка\n- 3 и id пользователя через пробел, если хотите написать конкретному пользователю.\nЗатем с новой строки введите текст сообщения",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Admin.sms)

@router.message(Admin.sms)
async def sms(messege: Message, state: FSMContext, session: AsyncSession):
    data, text = messege.text.split('\n')
    users_id = []
    if data.isdigit():
        users_id = await get_id_all_users(session)
    else:
        kod, x = data.split(' ')
        if(kod == '2'):
            users_id = await get_id_users(session, x) 
        elif kod == '3':
            users_id = [int(x),]
    from bot import bot as global_bot
    if global_bot is None:
        logging.error("Объект бота не инициализирован.")

    for i in users_id:
        try:
            await global_bot.send_message(i, text)
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение пользователю {i}: {e}")    
    await messege.answer(
        "Сообщение отправлено",
        reply_markup=make_row_keyboard(vozm)
    )
    await state.set_state(Admin.work)

# @router.message(Admin.work, F.text == vozm[9])
# async def del_uslug(messege: Message, state: FSMContext, session: AsyncSession):
#     await