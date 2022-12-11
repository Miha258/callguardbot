from aiogram import types
from aiogram.filters import Command
from aiogram import Router
from ....filters.in_black_list import InBlacklist
from ....keyboards.inline import account_markup
from ....filters.user_exist import UserExistFilter

auth_router_commands = Router()

    
@auth_router_commands.message(Command(commands=["start"]), InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))    
async def check_authorization_status(message: types.Message):
    user_id = message.from_user.id
    keyboard_markup = await account_markup(user_id)
    await message.answer("Ваш кабінет:", reply_markup = keyboard_markup)


@auth_router_commands.message(Command(commands=["start"]), UserExistFilter(user_exist = False), InBlacklist(in_blacklist = False))    
async def check_authorization_status(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
        [
            types.InlineKeyboardButton(text = "Клієнт", callback_data = "customer"),
            types.InlineKeyboardButton(text = "Охоронець", callback_data = "guard") 
        ]
    ])
    await message.answer("Вас вітає <b>Guard bot</b>.Зареєструйтесь в системі як:", reply_markup = keyboard_markup)