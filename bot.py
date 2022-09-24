from aiogram import Bot
from config import API_TOKEN

PARSE_MODE = "HTML"

bot = Bot(token = API_TOKEN, parse_mode=PARSE_MODE)