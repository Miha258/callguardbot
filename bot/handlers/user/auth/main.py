from aiogram import types
from aiogram import Router
from aiogram.fsm.context import FSMContext
from .state import CreateAccount
from ....database.classes.customer import Customer
from ....database.classes.guards import Guards
from ....keyboards.inline import account_markup, get_cities_markup, send_terms
from bot.misc.bot import bot
from bot.misc.utils.cities import get_cities
from ....filters.user_exist import UserExistFilter
from ....filters.is_phone import ValidtePhone

from .commands import auth_router_commands
from .callback_query import auth_router_callbacks
from bot.misc.bot import API_TOKEN

auth_router = Router()
auth_router.include_router(auth_router_commands)
auth_router.include_router(auth_router_callbacks)


@auth_router.message(CreateAccount.fullname, UserExistFilter(user_exist = False))
async def choose_city(message: types.Message, state: FSMContext):
    await state.update_data({"fullname": message.text})
    await state.set_state(CreateAccount.photo)
    await message.answer('Скиньте ваше фото:')


@auth_router.message(CreateAccount.photo, UserExistFilter(user_exist = False))
async def set_photo(message: types.Message, state: FSMContext):
    if message.photo:
        await state.update_data({"photo": message.photo[0].file_id})
        await state.set_state(CreateAccount.city)
        await message.answer('Виберіть місто із списку:', reply_markup = get_cities_markup())
    else:
        await message.answer('Скиньте ваше фото ще раз')


@auth_router.message(CreateAccount.phone, ValidtePhone(is_phone = True))
async def enter_phone(message: types.Message, state: FSMContext):
    await state.update_data({"phone": message.text})
    data = await state.get_data()

    if data['user_type'] == 'guard':
        await state.set_state(CreateAccount.description)
        await message.answer('Тепер розкажіть про себе і свій досвід:')
    
    elif data['user_type'] == 'customer':
        await state.set_state(CreateAccount.accept_terms)
        await send_terms(message)
         


@auth_router.message(CreateAccount.description)
async def set_decription(message: types.Message, state: FSMContext):
    await state.update_data({"description": message.text})
    await state.set_state(CreateAccount.accept_terms)
    await send_terms(message)
    



