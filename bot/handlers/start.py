from aiogram import Router, Dispatcher, types, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot.handlers.states import StartBot

from bot.db.requests import ensure_user, get_user_by_id

router = Router(name="Start Router")

bike_parks = ["Шерегеш байк-парк", "Белка в колесе"]

def make_row_keyboard(items: list[str], kol_bt: int = 2) -> ReplyKeyboardMarkup:
    keyboard = [items[i:i + kol_bt] for i in range (0, len(items), kol_bt)]
    keyboard = [[KeyboardButton(text=item) for item in row] for row in keyboard]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    user = await ensure_user(session, message.from_user.id)
    if user is not None:
        await message.answer(
            f"{user[0]} Добро пожаловать\nВыберите интересующий вас байк парк",
            reply_markup=make_row_keyboard(bike_parks)
        )
    else:
        await message.answer(
            "Добро пожаловать. Для начало введите свое Имя и Фамилию, чтобы я знал как к Вам обращаться, и свой номер телефона, чтобы мы моли в случае чего связаться с вами"
        )
        await state.set_state(StartBot.registr)

@router.message(StartBot.registr)
async def reg(message: Message, state: FSMContext, session: AsyncSession):
    state.clear()
    data = message.text.split(' ')
    user = await get_user_by_id(session, message.from_user.id)
    user.name = data[0]
    user.famaly = data[1]
    user.namber = data[2]
    await session.commit()
    await message.answer(
            "Данныне сохранены\nТеперь Вы можете выбрать интересующий вас байк парк",
            reply_markup=make_row_keyboard(bike_parks)
    )
    

@router.message(Command("user"))
async def bikePark(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Выберите интересующий вас байк парк",
        reply_markup=make_row_keyboard(bike_parks)
    )