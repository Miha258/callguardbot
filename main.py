from bot import bot
from aiogram import Dispatcher
from aiogram.filters import Command
from funcs.auth import *
from funcs.account import *
import logging
import asyncio
from funcs.auth import auth_router
from funcs.account import account_router
from funcs.alarm import alarm_router
from funcs.responds import responds_router
from funcs.paynaments import paynaments_router
from funcs.admin import admin_router
    
@auth_router.message(Command(commands=["start"]))    
async def check_authorization_status(message: types.Message):
    user_id = message.from_user.id
    
    if not await Customer.check_user_exists(user_id) and not await Guards.check_user_exists(user_id):
        keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
            [
                types.InlineKeyboardButton(text = "Клієнт", callback_data = "customer"),
                types.InlineKeyboardButton(text = "Охоронець", callback_data = "guard") 
            ]
        ])
        await message.answer("Вас вітає <b>Guard bot</b>.Зареєструйтесь в системі як:", reply_markup = keyboard_markup)
    else:
        keyboard_markup = await get_user_account_markup(user_id)
        await message.answer("Ваш кабінет:", reply_markup = keyboard_markup)

    
async def main():
    dp = Dispatcher()
    dp.include_router(auth_router)
    dp.include_router(account_router)
    dp.include_router(alarm_router)
    dp.include_router(responds_router)
    dp.include_router(paynaments_router)
    dp.include_router(admin_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())