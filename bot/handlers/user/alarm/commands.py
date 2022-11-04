from aiogram import types
from aiogram.filters import Command
from aiogram import Router
from ....filters.in_black_list import InBlacklist
from ....filters.user_exist import UserExistFilter
from ....misc.utils.alarm import get_alarm_customer, get_alarm_guards, get_alarm_status, get_alarm_by_customer_id, get_from_accepted_alarms, is_alarm_exists

alarm_router_commands = Router()


@alarm_router_commands.message(Command(commands=["alarm_status"]), InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))    
async def get_alarm_status_command(message: types.Message):
    user_id = message.from_user.id
    alarm_id = get_alarm_by_customer_id(user_id) or int(get_from_accepted_alarms(user_id))
     
    if is_alarm_exists(alarm_id):
        alarm_status = get_alarm_status(alarm_id)
        await message.answer(f'Статус замовлення: {alarm_status}')
    else:
        await message.answer('На даний момент у вас немає активного замовлення')
    