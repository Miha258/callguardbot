from funcs.account import get_user_account_markup
from mongodb import BaseUser, BlackList, Customer, Guards
from aiogram import types
from validator import *
from aiogram import Router
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .account import get_cities_markup

auth_router = Router()
 
class CreateAccount(StatesGroup):
    fullname = State()
    city = State()
    phone = State()
    description = State()
    user_respond = State()


@auth_router.callback_query(F.data.in_({'customer', 'guard'}))
async def choose_registration_type(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    user_id = query.from_user.id

    if await Guards.check_user_exists(user_id):
        await query.message.delete()
        await query.message.answer('Ви вже зареєстровані як <b>охоронець</b>.')

    elif await Customer.check_user_exists(user_id):
        await query.message.delete()
        await query.message.answer('Ви вже зареєстровані як <b>клієнт</b>.')

    elif not await BlackList.is_in(user_id):
        if answer_data == 'customer':
            await state.set_data({"user_type": 'customer'})

        elif answer_data == 'guard':
            await state.set_data({"user_type": 'guard'})
        await state.set_state(CreateAccount.fullname)
        await query.message.answer('Введіть ПІБ:')
    else:
        await query.message.answer('Ви в чс!')


@auth_router.message(CreateAccount.fullname)
async def choose_registration_type(message: types.Message, state: FSMContext):
    keyboard_markup = get_cities_markup()

    await state.update_data({"fullname": message.text})
    await state.set_state(CreateAccount.city)
    await message.answer(f'Введіть ваше місто.Виберіть нове місто із списку:', reply_markup = keyboard_markup)


@auth_router.callback_query(CreateAccount.city, F.data.in_(get_cities()))
async def choose_registration_type(query: types.CallbackQuery, state: FSMContext):
    await state.update_data({"city": query.data})
    await state.set_state(CreateAccount.phone)
    await query.message.answer('Введіть ваш телефон:')


@auth_router.message(CreateAccount.phone)
async def choose_registration_type(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if validate_phone(message.text):
        await state.update_data({"phone": message.text})
        data = await state.get_data()

        if data['user_type'] == 'guard':
            await state.set_state(CreateAccount.description)
            await message.answer('Тепер розкажіть про себе і свій досвід:')
        
        elif data['user_type'] == 'customer':
            del data['user_type']
            data['_id'] = message.from_user.id
            data['activated'] = False

            await Customer.insert(data)
            await state.clear() 
            await message.answer('Ви успішно зареєстувалися як <b>клієнт</b>.')

            keyboard_markup = await get_user_account_markup(user_id)
            await message.answer("Ваш кабінет:", reply_markup = keyboard_markup)
    else:
        await message.answer('Невірний номер, спробуйие ще раз:')

@auth_router.message(CreateAccount.description)
async def choose_registration_type(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    await state.update_data({"description": message.text})
    data = await state.get_data()
    
    del data['user_type']
    data['_id'] = message.from_user.id

    await Guards.insert(data)
    await state.clear()
    await message.answer('Ви успішно зареєстувалися як <b>охоронець</b>.')
    keyboard_markup = await get_user_account_markup(user_id)
    await message.answer("Ваш кабінет:", reply_markup = keyboard_markup)
    


