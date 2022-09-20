from funcs.account import get_user_account_markup
from mongodb import Customer, Guards
from aiogram import types
from validator import *
from aiogram import Router
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

auth_router = Router()
 
class CreateAccount(StatesGroup):
    fullname = State()
    city = State()
    phone = State()
    description = State()


@auth_router.callback_query(F.data.in_({'customer', 'guard'}))
async def choose_registration_type(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    
    if answer_data == 'customer':
        await state.set_data({"user_type": 'customer'})

    elif answer_data == 'guard':
        await state.set_data({"user_type": 'guard'})
    await state.set_state(CreateAccount.fullname)
    await query.message.answer('Введіть ПІБ:')


@auth_router.message(CreateAccount.fullname)
async def choose_registration_type(message: types.Message, state: FSMContext):
    await state.update_data({"fullname": message.text})
    await state.set_state(CreateAccount.city)
    await message.answer(f'Введіть ваше місто.Виберіть нове місто із списку ({" ,".join(get_cities())}):')


@auth_router.message(CreateAccount.city)
async def choose_registration_type(message: types.Message, state: FSMContext):
    await state.update_data({"city": message.text})
    await state.set_state(CreateAccount.phone)
    await message.answer('Введіть ваш телефон:')


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

            await Customer.insert(data)
            await state.clear()
            await message.answer('Ви успішно зареєстувалися як <b>користувач</b>.')

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
    


