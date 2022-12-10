from bot.misc.bot import bot
from aiogram import Router
from aiogram.fsm.context import FSMContext
from ...database.classes.blacklist import BlackList
from ...database.classes.customer import Customer
from ...database.classes.baseuser import BaseUser
from ...database.classes.guards import Guards
from ...misc.utils.cities import *
from .state import AdminState
from aiogram import types
from aiogram import F
from aiogram.filters import Command
from ...filters.is_admin import AdminFilter

admin_router = Router()


@admin_router.message(AdminState.add_city, AdminFilter(is_admin = True))
async def add_city_handler(message: types.Message, state: FSMContext):
    try:
        city, chat_id = message.text.split('-', 1)
        add_city(city.replace(' ', ''), int(chat_id))

        await state.clear()
        await message.answer('Список міст оновлено👍🏻.')
    except Exception:
        await message.answer('Неправильний формат!')



@admin_router.message(AdminState.remove_city, AdminFilter(is_admin = True))
async def remove_city_handler(message: types.Message, state: FSMContext):
    remove_city(message.text)
    await state.clear()
    await message.answer('Список міст оновлено👍🏻.')
    


@admin_router.message(AdminState.ban_user, AdminFilter(is_admin = True))
async def ban_user_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    banned_user = await Guards.get(user_id) or await Customer.get(user_id)
    cities = get_cities()
    chat_id = cities[banned_user['city']]
    
    await BaseUser.delete(user_id)
    await BlackList.add(user_id)
    
    await bot.ban_chat_member(chat_id, user_id)
    
    await state.clear()
    await message.answer('Користувача забанено👍🏻.')
    await bot.send_message(chat_id = user_id, text = 'Вас забанено!')


@admin_router.message(Command(commands=['admin']), AdminFilter(is_admin = True))
async def admin_command_handler(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
        [
            types.InlineKeyboardButton(text = "Додати місто", callback_data = "add_city"),
            types.InlineKeyboardButton(text = "Видалити місто", callback_data = "remove_city"),
            types.InlineKeyboardButton(text = "Забанити користувача", callback_data = "ban_user"),
        ]
    ])
    await message.answer('Admin panel:', reply_markup = keyboard_markup)


@admin_router.callback_query(F.data == 'add_city')
async def add_city_handler(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.add_city)
    await query.message.answer('Додайте місто у форматі: "city" - "group_id": ')


@admin_router.callback_query(F.data == 'remove_city')
async def remove_city_handler(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.remove_city)
    await query.message.answer('Введіть назву міста:')


@admin_router.callback_query(F.data == 'ban_user')
async def ban_user_handler(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.ban_user)
    await query.message.answer('Введіть айді користувача для бану:')