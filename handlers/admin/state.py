from aiogram.fsm.state import State, StatesGroup

class AdminState(StatesGroup):
    add_city = State()
    remove_city = State()
    ban_user = State()