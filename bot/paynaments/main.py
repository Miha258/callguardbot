from .wayforpay import get_invoice_url
from aiogram import F
from aiogram import Router
from bot.filters.in_black_list import InBlacklist
from bot.filters.user_exist import UserExistFilter
from aiogram import types
from ..keyboards.inline import get_guard_access_markup

paynament_router = Router()


@paynament_router.callback_query(F.data == 'get_guard_access', InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))
async def alarm_handler(query: types.CallbackQuery):
    user_id = query.from_user.id
    url = get_invoice_url(user_id)

    keyboard_markup = get_guard_access_markup(user_id, url)
    await query.message.answer("Тепер перейдіть по посиланню для оплати послуги:", reply_markup = keyboard_markup)