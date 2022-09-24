from funcs.account import get_user_account_markup
from mongodb import Customer, UserResponds
from aiogram import types
from validator import *
from aiogram import Router
from aiogram import F
from aiogram.fsm.context import FSMContext
from .alarm import AlarmState
from config import get_alarm_by_customer_id, get_alarm_guards, remove_alarm


responds_router = Router()

@responds_router.callback_query(F.data == 'leave_respond')
async def leave_respond_handler(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(AlarmState.user_respond)
    await query.message.answer('Напишіть відгук:')
    

@responds_router.message(AlarmState.user_respond)
async def get_respond_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    alarm_id = get_alarm_by_customer_id(user_id)
    
    customer = await Customer.get(user_id)
    
    await state.clear()
    guards = get_alarm_guards(alarm_id)

    for guard in guards:
        await UserResponds.new(guard, customer['fullname'], customer['city'], message.text)

    remove_alarm(alarm_id)
    await message.answer('Відгук залишено👍🏻. ')
    await message.answer('Ваш кібінет:', reply_markup = await get_user_account_markup(user_id))

