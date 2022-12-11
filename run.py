from bot.misc.bot import API_TOKEN, bot
from aiogram import Dispatcher, Bot
from aiogram.types import InputFile
import logging, ssl
from aiohttp import web
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    TokenBasedRequestHandler,
    setup_application
)
from bot.handlers.admin.main import admin_router
from bot.handlers.user.auth.main import auth_router
from bot.handlers.user.account.main import account_router
from bot.handlers.user.responds.main import responds_router
from bot.handlers.user.alarm.main import alarm_router
from bot.paynaments.main import paynament_router
import requests

from bot.paynaments.server import handle_paynament

BASE_URL = "https://edossecurity.com"
WEB_SERVER_HOST = "edossecurity.com"
WEB_SERVER_PORT = 443
# MAIN_BOT_PATH = "/webhook/main/"
MAIN_BOT_PATH = "/" # add / 
OTHER_BOTS_PATH = "/webhook/bot/{bot_token}"

# PUBLIC CERT
# WEBHOOK_SSL_CERT = 'c:\\guardsbot\\BUY_public.pem'  # Path to the ssl certificate
# WEBHOOK_SSL_PRIV = 'c:\\guardsbot\\BUY_private.key'  # Path to the ssl private key

# SELF CERT
WEBHOOK_SSL_CERT = 'c:\\guardsbot\\YOURPUBLIC.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = 'c:\\guardsbot\\YOURPRIVATE.key'  # Path to the ssl private key

# SETUP WEBHOOK
async def on_startup(dispatcher: Dispatcher, bot: Bot):
    # UPLOAD CERT AND SETUP HOOK
    url = 'https://api.telegram.org/bot{API_TOKEN}/setWebhook'
    file = {'file': open(WEBHOOK_SSL_CERT,'rb')}
    form_data ={"URL": "{BASE_URL}:{WEB_SERVER_PORT}{MAIN_BOT_PATH}"}
    requests.post(url=url, data=form_data, files=file) 
    # await bot.set_webhook(f"{BASE_URL}:{WEB_SERVER_PORT}{MAIN_BOT_PATH}",certificate=open(WEBHOOK_SSL_CERT, 'rb')) # ONLY WORK WEBHOOK PATH !!!!! BUT NOT WORK  CERT UPLOAD! SO UPLOAD CERT MANULAY FROM MULTIPART HTML PAGE REQUEST UPLOAD>HTML
      
def main():
    session = AiohttpSession()
    bot_settings = {"session": session, "parse_mode": "HTML"}

    dp = Dispatcher()
    dp.include_router(auth_router)
    dp.include_router(account_router) 
    dp.include_router(alarm_router)
    dp.include_router(responds_router)
    dp.include_router(admin_router)
    dp.include_router(paynament_router)
    dp.startup.register(on_startup)

    app = web.Application()
    app.router.add_post('/paynament', handle_paynament)

    SimpleRequestHandler(dispatcher = dp, bot = bot).register(app, path = MAIN_BOT_PATH)
    TokenBasedRequestHandler(dispatcher = dp, bot_settings = bot_settings).register(app, path = OTHER_BOTS_PATH)
 
    setup_application(app, dp, bot = bot)

    # Generate SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
    web.run_app(app, host = "edossecurity.com" , port = WEB_SERVER_PORT, ssl_context = context)

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    main()