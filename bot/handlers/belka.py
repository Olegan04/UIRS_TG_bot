from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from bot.db.requests import create_reservation
from bot.handlers.states import Belka
from bot.handlers.data import month, dayInMounth, days, months, uslTime, do_in_belka, uslug_in_belka
from bot.handlers.data import akip_belka, clook, bikes_belka, time_belka, instruktor_belka, abonement_belka

router = Router(name="ActionBelka")

def make_row_keyboard(items: list[str], kol_bt: int = 2) -> ReplyKeyboardMarkup:
    keyboard = [items[i:i + kol_bt] for i in range (0, len(items), kol_bt)]
    keyboard = [[KeyboardButton(text=item) for item in row] for row in keyboard]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(F.text == "Белка в колесе")
async def cmd_belka(message: Message, state: FSMContext):
    await message.answer(
        "Хороший выбр. Что Вас интересует?",
        reply_markup=make_row_keyboard(do_in_belka)
    )
    await state.set_state(Belka.action)

@router.message(Belka.action, F.text == do_in_belka[0])
async def shInf(message: Message, state: FSMContext):
    await message.answer(
        "Данный байк парк находится в Белокурихе в лесной заимке",
        reply_markup=make_row_keyboard([do_in_belka[1],])
    )

@router.message(Belka.action, F.text == do_in_belka[1])
async def shUslug(message: Message, state: FSMContext):
    date = datetime.now()
    m = date.month
    if(m < 9):
        await message.answer(
            "Наш байк парк предоставляет следующие услуги:",
            reply_markup=make_row_keyboard(uslug_in_belka)
        )
        await state.set_state(Belka.uslug)
    else:
        await message.answer(
            "К сожалению в этом сезоне байк парк уже не работает("
        )

@router.message(Belka.uslug, F.text == uslug_in_belka[0])
async def bikePas(message: Message, state: FSMContext):
    await state.update_data(uslug = 'Заброс')
    await message.answer(
        "Выберите время",
        reply_markup=make_row_keyboard(clook, 3)
    )
    await state.set_state(Belka.mounth)

@router.message(Belka.uslug, F.text == uslug_in_belka[1])
async def bike(message: Message, state: FSMContext):
    await state.update_data(uslug = 'Велосипед')
    await message.answer(
        "Выберите интересующий вас велосипед",
        reply_markup=make_row_keyboard(bikes_belka)
    )
    await state.set_state(Belka.vTime)

@router.message(Belka.uslug, F.text == uslug_in_belka[2])
async def akipBron(message: Message, state: FSMContext):
    await message.answer(
        "Выберите какую экиперовку вы хотите забронировать",
        reply_markup=make_row_keyboard(akip_belka)
    )
    await state.set_state(Belka.vTime)

@router.message(Belka.vTime, F.text.in_(bikes_belka))
async def times(message: Message, state: FSMContext):
    await state.update_data(bike = message.text)
    await message.answer(
        "Выберите на какое время вам нужно забронировать велосипед",
        reply_markup=make_row_keyboard(time_belka)
    )
    await state.set_state(Belka.mounth)

@router.message(Belka.vTime, F.text.in_(akip_belka))
async def times(message: Message, state: FSMContext):
    await state.update_data(uslug = message.text)
    await message.answer(
        "Выберите на какое время вам нужно забронировать экиперовку",
        reply_markup=make_row_keyboard(time_belka)
    )
    await state.set_state(Belka.mounth)

@router.message(Belka.mounth, F.text.in_(clook))
async def brone(message: Message, state: FSMContext):
    await state.update_data(time = message.text.lower())
    await state.update_data(pas = "на спуск")
    date = datetime.now()
    m = date.month - 6
    if (m < 0):
        m = 0
    m_list = months[m:]
    await message.answer(
        "Выберите месяц",
        reply_markup=make_row_keyboard(m_list)
    )
    await state.set_state(Belka.day)

@router.message(Belka.mounth)
async def brone(message: Message, state: FSMContext):
    await state.update_data(pas = message.text.lower())
    date = datetime.now()
    m = date.month - 6
    if (m < 0):
        m = 0
    m_list = months[m:]
    await message.answer(
        "Выберите месяц",
        reply_markup=make_row_keyboard(m_list)
    )
    await state.set_state(Belka.day)

@router.message(Belka.day, F.text.in_(months))
async def day(message: Message, state:FSMContext):
    await state.update_data(mounth = message.text.lower())
    user_data = await state.get_data()
    d_list = days[0:dayInMounth[user_data['mounth']]]
    await message.answer(
        "Выберите день",
        reply_markup=make_row_keyboard(d_list, 6)
    )
    user_data = await state.get_data()
    if 'time' is user_data:
        await state.set_state(Belka.utog)
    else:
        await state.set_state(Belka.time)

@router.message(Belka.time, F.text.in_(days))
async def timeStart(message: Message, state:FSMContext):
    await state.update_data(day = message.text)
    await message.answer(
        "Выбирите примерное время когда Вы приедите",
        reply_markup=make_row_keyboard(clook, 3)
    )
    await state.set_state(Belka.utog)

@router.message(Belka.utog)
async def day(message: Message, state:FSMContext, session: AsyncSession):
    date = datetime.now()
    user_data = await state.get_data()
    if 'day' not in  user_data:
        user_data['day'] = message.text
    else:
        user_data['time'] = message.text

    if 'bike' in user_data:
        await create_reservation(session, message.from_user.id, 
                                user_data['uslug'], uslTime[user_data["pas"]], "Белокуриха", 
                                datetime(date.year, month[user_data['mounth']], int(user_data['day'])),
                                datetime.strptime(user_data['time'], "%H:%M").time(), nameBike=user_data['bike'])
    else:
        await create_reservation(session, message.from_user.id, 
                                user_data['uslug'], uslTime[user_data["pas"]], "Белокуриха", 
                                datetime(date.year, month[user_data['mounth']], int(user_data['day'])),
                                datetime.strptime(user_data['time'], "%H:%M").time())
    await state.clear()
    await message.answer(
        "Байкпас сохранен. Выберите дальнейшее действие",
        reply_markup=make_row_keyboard(do_in_belka)
    )
    await state.set_state(Belka.action)