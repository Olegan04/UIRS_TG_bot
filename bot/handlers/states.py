from aiogram.fsm.state import StatesGroup, State

class StartBot(StatesGroup):
    registr = State()

class Sheregesh(StatesGroup):
    actionGesh = State()
    uslug = State()
    vTime = State()
    mounth = State()
    day = State()
    time = State() 
    utog = State()

class Belka(StatesGroup):
    action = State()
    uslug = State()
    vTime = State()
    mounth = State()
    day = State()
    time = State() 
    utog = State()

class Admin(StatesGroup):
    login = State()
    work = State()
    new_uslug = State()
    corect_uslug = State()
    save_change_uslug = State()
    del_uslug = State()
    corect_bike = State()
    save_change_bike = State()
    new_bike = State()
    del_bike = State()
    bron_date = State()
    sms = State()
