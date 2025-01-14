from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from bot.db.requests import create_reservation
from bot.handlers.states import Sheregesh, Belka
from bot.handlers.data import hours, munuts, month, dayInMounth, days, months, uslTime, do_in_sheregesh, abonement_sheregesh
from bot.handlers.data import uslug_in_sheregesh, time_sheregesh, bikes_sheregesh, akip_sheregesh, instruktor_sheregesh
router = Router(name="ActionGesh")

clok = []

def cloke():
    for i in hours:
        for j in munuts:
            clok.append(i+":"+j)

def make_row_keyboard(items: list[str], kol_bt: int = 2) -> ReplyKeyboardMarkup:
    keyboard = [items[i:i + kol_bt] for i in range (0, len(items), kol_bt)]
    keyboard = [[KeyboardButton(text=item) for item in row] for row in keyboard]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(F.text == "Шерегеш байк-парк")
async def cmd_gesh(message: Message, state: FSMContext):
    cloke()
    await message.answer(
        "Хороший выбр. Что Вас интересует?",
        reply_markup=make_row_keyboard(do_in_sheregesh)
    )
    await state.set_state(Sheregesh.actionGesh)

@router.message(Sheregesh.actionGesh, F.text == do_in_sheregesh[0])
async def shInf(message: Message, state: FSMContext):
    await message.answer(
        "Данный байк парк на Секторе Е в Шерегеше",
        reply_markup=make_row_keyboard([do_in_sheregesh[1],])
    )

@router.message(Sheregesh.actionGesh, F.text == do_in_sheregesh[1])
async def shUslug(message: Message, state: FSMContext):
    date = datetime.now()
    m = date.month
    if(m < 9):
        await message.answer(
            "Наш байк парк предоставляет следующие услуги:",
            reply_markup=make_row_keyboard(uslug_in_sheregesh)
        )
        await state.set_state(Sheregesh.uslug)
    else:
        await message.answer(
            "К сожалению в этом сезоне байк парк уже не работает("
        )

@router.message(Sheregesh.uslug, F.text == uslug_in_sheregesh[0])
async def bikePas(message: Message, state: FSMContext):
    await state.update_data(uslug = 'Байк-пасс')
    await message.answer(
        "Выберите интересующий вас байкпас",
        reply_markup=make_row_keyboard(time_sheregesh)
    )
    await state.set_state(Sheregesh.mounth)

@router.message(Sheregesh.uslug, F.text == uslug_in_sheregesh[1])
async def bike(message: Message, state: FSMContext):
    await state.update_data(uslug = 'Велосипед')
    await message.answer(
        "Выберите интересующий вас велосипед",
        reply_markup=make_row_keyboard(bikes_sheregesh)
    )
    await state.set_state(Sheregesh.vTime)

@router.message(Sheregesh.uslug, F.text == uslug_in_sheregesh[2])
async def akipBron(message: Message, state: FSMContext):
    await message.answer(
        "Выберите какую экиперовку вы хотите забронировать",
        reply_markup=make_row_keyboard(akip_sheregesh)
    )
    await state.set_state(Sheregesh.vTime)

@router.message(Sheregesh.uslug, F.text == uslug_in_sheregesh[3])
async def instr(message: Message, state: FSMContext):
    await message.answer(
        "Выберите вид занятия",
        reply_markup=make_row_keyboard(instruktor_sheregesh)
    )
    await state.set_state(Sheregesh.mounth)

@router.message(Sheregesh.vTime, F.text.in_(bikes_sheregesh))
async def times(message: Message, state: FSMContext):
    await state.update_data(bike = message.text)
    await message.answer(
        "Выберите на какое время вам нужно забронировать велосипед",
        reply_markup=make_row_keyboard(time_sheregesh)
    )
    await state.set_state(Sheregesh.mounth)

@router.message(Sheregesh.vTime, F.text.in_(akip_sheregesh))
async def times(message: Message, state: FSMContext):
    await state.update_data(uslug = message.text)
    await message.answer(
        "Выберите на какое время вам нужно забронировать экиперовку",
        reply_markup=make_row_keyboard(time_sheregesh)
    )
    await state.set_state(Sheregesh.mounth)

@router.message(Sheregesh.mounth)
async def brone(message: Message, state: FSMContext):
    date = datetime.now()
    s = message.text
    if(s == instruktor_sheregesh[0]):
        await state.update_data(uslug = "ИнструкторНовичок", pas = "на спуск")
    elif(s == instruktor_sheregesh[1]):
        await state.update_data(uslug = "ИнструкторСтандарт", pas = "1_час")
    else:
        await state.update_data(pas = message.text.lower())
    m = date.month  - 6
    if (m < 0):
        m = 0
    m_list = months[m:]
    await message.answer(
        "Выберите месяц",
        reply_markup=make_row_keyboard(m_list)
    )
    await state.set_state(Sheregesh.day)

@router.message(Sheregesh.day, F.text.in_(months))
async def day(message: Message, state:FSMContext):
    await state.update_data(mounth = message.text.lower())
    user_data = await state.get_data()
    d_list = days[0:dayInMounth[user_data['mounth']]]
    await message.answer(
        "Выберите день",
        reply_markup=make_row_keyboard(d_list, 6)
    )
    await state.set_state(Sheregesh.time)

@router.message(Sheregesh.time, F.text.in_(days))
async def timeStart(message: Message, state:FSMContext):
    await state.update_data(day = message.text)
    await message.answer(
        "Выбирите примерное время когда Вы приедите",
        reply_markup=make_row_keyboard(clok, 4)
    )
    await state.set_state(Sheregesh.utog)

@router.message(Sheregesh.utog, F.text.in_(clok))
async def day(message: Message, state:FSMContext, session: AsyncSession):
    await state.update_data(time = message.text)
    date = datetime.now()
    user_data = await state.get_data()

    if 'bike' in user_data:
        await create_reservation(session, message.from_user.id, 
                                user_data['uslug'], uslTime[user_data["pas"]], "Шерегеш", 
                                datetime(date.year-1, month[user_data['mounth']], int(user_data['day'])),
                                datetime.strptime(user_data['time'], "%H:%M").time(), nameBike=user_data['bike'])
    else:
        await create_reservation(session, message.from_user.id, 
                                user_data['uslug'], uslTime[user_data["pas"]], "Шерегеш", 
                                datetime(date.year-1, month[user_data['mounth']], int(user_data['day'])),
                                datetime.strptime(user_data['time'], "%H:%M").time())
    await state.clear()
    await message.answer(
        "Услуга сохранена. Выберите дальнейшее действие",
        reply_markup=make_row_keyboard(do_in_sheregesh)
    )
    await state.set_state(Sheregesh.actionGesh)