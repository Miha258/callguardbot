from aiogram.fsm.state import State, StatesGroup

class CreateAccount(StatesGroup):
    fullname = State()
    city = State()
    phone = State()
    description = State()
    user_respond = State()
