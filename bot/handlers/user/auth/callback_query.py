from aiogram import F
from aiogram import Router
from aiogram import types
from .state import CreateAccount
from aiogram.fsm.context import FSMContext
from ....filters.user_exist import UserExistFilter
from ....filters.in_black_list import InBlacklist
from bot.misc.utils.cities import get_cities

auth_router_callbacks = Router()


@auth_router_callbacks.callback_query(F.data.in_({'customer', 'guard'}), UserExistFilter(user_exist = False), InBlacklist(in_blacklist = False))
async def choose_registration_type(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data

    if answer_data == 'customer':
        await state.set_data({"user_type": 'customer'})

    elif answer_data == 'guard':
        await state.set_data({"user_type": 'guard'})
    await state.set_state(CreateAccount.fullname)
    await query.message.answer('Введіть ПІБ:')


@auth_router_callbacks.callback_query(CreateAccount.city, F.data.func(lambda data: data in get_cities()))
async def choose_city(query: types.CallbackQuery, state: FSMContext):
    await state.update_data({"city": query.data})
    await state.set_state(CreateAccount.phone)
    await query.message.answer('Введіть ваш телефон:')
    