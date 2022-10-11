from bot.misc.bot import bot
from aiogram import Dispatcher, Bot   
import logging
from aiohttp import web
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    TokenBasedRequestHandler,
    setup_application,

)
from bot.handlers.admin.main import admin_router
from bot.handlers.user.auth.main import auth_router
from bot.handlers.user.account.main import account_router
from bot.handlers.user.responds.main import responds_router
from bot.handlers.user.alarm.main import alarm_router


BASE_URL =" www.edossecurity.com"
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = 80
MAIN_BOT_PATH = "/webhook/main"
OTHER_BOTS_PATH = "/webhook/bot/{bot_token}"


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    await bot.set_webhook(f"{BASE_URL}{MAIN_BOT_PATH}")
  

def main():
    session = AiohttpSession()
    bot_settings = {"session": session, "parse_mode": "HTML"}

    dp = Dispatcher() 
    dp.include_router(auth_router)
    dp.include_router(account_router) 
    dp.include_router(alarm_router)
    dp.include_router(responds_router)
    dp.include_router(admin_router)
    dp.startup.register(on_startup)


    app = web.Application()
    SimpleRequestHandler(dispatcher = dp, bot = bot).register(app, path = MAIN_BOT_PATH)
    TokenBasedRequestHandler(dispatcher = dp, bot_settings = bot_settings).register(app, path = OTHER_BOTS_PATH)

    setup_application(app, dp, bot = bot)
    web.run_app(app, host = WEB_SERVER_HOST, port = WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    main()