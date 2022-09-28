from bot.misc.bot import bot
from aiogram import Dispatcher
import logging
import asyncio

from bot.handlers.admin.main import admin_router
from bot.handlers.user.auth.main import auth_router
from bot.handlers.user.account.main import account_router
from bot.handlers.user.responds.main import responds_router
from bot.handlers.user.alarm.main import alarm_router


    
async def main():
    dp = Dispatcher()
    dp.include_router(auth_router)
    dp.include_router(account_router) 
    dp.include_router(alarm_router)
    dp.include_router(responds_router)
    # dp.include_router(paynaments_router)
    dp.include_router(admin_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())