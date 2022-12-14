from aiogram.fsm.state import State, StatesGroup

class AlarmState(StatesGroup):
    amount_of_guards = State()
    explain_reason = State()
    get_user_location = State()
    user_respond = State()
