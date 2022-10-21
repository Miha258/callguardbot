from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.state import State, StatesGroup


class AccountEdits(StatesGroup):
    fullname = State()
    photo = State()
    description = State()
    city = State()
