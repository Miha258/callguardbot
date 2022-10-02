from aiogram import types
from aiogram import Router
from aiogram import F
from bot.misc.bot import bot
from .state import CreateAccount
from ....keyboards.inline import get_cities_markup
from aiogram.fsm.context import FSMContext
from ....database.classes.customer import Customer
from ....database.classes.guards import Guards
from ....keyboards.inline import account_markup
from aiogram.filters import Command
from ....misc.utils.cities import get_cities
from ....filters.user_exist import UserExistFilter
from ....filters.is_phone import ValidtePhone
from ....filters.in_black_list import InBlacklist


auth_router = Router()


@auth_router.message(CreateAccount.fullname, UserExistFilter(user_exist = False))
async def choose_registration_type(message: types.Message, state: FSMContext):
    keyboard_markup = get_cities_markup()
    
    await state.update_data({"fullname": message.text})
    await state.set_state(CreateAccount.city)
    await message.answer(f'Введіть ваше місто.Виберіть нове місто із списку:', reply_markup = keyboard_markup)


@auth_router.message(CreateAccount.phone, ValidtePhone(is_phone = True))
async def enter_phone(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

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

        keyboard_markup = await account_markup(user_id)
        await message.answer("Ваш кабінет:", reply_markup = keyboard_markup)
   
        
@auth_router.message(CreateAccount.description)
async def set_decription(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    await state.update_data({"description": message.text})
    data = await state.get_data()
    
    del data['user_type']
    data['_id'] = message.from_user.id

    await Guards.insert(data)
    await state.clear()
    await message.answer('Ви успішно зареєстувалися як <b>охоронець</b>.')

    city_id = get_cities()[data['city']]
    invite_invite = await bot.create_chat_invite_link(city_id)
    await message.answer('Тепер вам потрібно зайти в групу охоронців, щоб відсідковувати замовлення:', 
        reply_markup = types.InlineKeyboardMarkup(inline_keyboard = [[
            types.InlineKeyboardButton(text = "Приєднатися", url = invite_invite.invite_link)
        ]
    ]
    ),)

    keyboard_markup = await account_markup(user_id)
    await message.answer("Ваш кабінет:", reply_markup = keyboard_markup)


@auth_router.message(Command(commands=["start"]), InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))    
async def check_authorization_status(message: types.Message):
    user_id = message.from_user.id
    keyboard_markup = await account_markup(user_id)
    await message.answer("Ваш кабінет:", reply_markup = keyboard_markup)


@auth_router.message(Command(commands=["start"]), UserExistFilter(user_exist = False), InBlacklist(in_blacklist = False))    
async def check_authorization_status(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
        [
            types.InlineKeyboardButton(text = "Клієнт", callback_data = "customer"),
            types.InlineKeyboardButton(text = "Охоронець", callback_data = "guard") 
        ]
    ])
    await message.answer("Вас вітає <b>Guard bot</b>.Зареєструйтесь в системі як:", reply_markup = keyboard_markup)
    


@auth_router.callback_query(F.data.in_({'customer', 'guard'}), UserExistFilter(user_exist = False), InBlacklist(in_blacklist = False))
async def choose_registration_type(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data

    if answer_data == 'customer':
        await state.set_data({"user_type": 'customer'})

    elif answer_data == 'guard':
        await state.set_data({"user_type": 'guard'})
    await state.set_state(CreateAccount.fullname)
    await query.message.answer('Введіть ПІБ:')


@auth_router.callback_query(CreateAccount.city, F.data.func(lambda data: data in get_cities()))
async def choose_city(query: types.CallbackQuery, state: FSMContext):
    await state.update_data({"city": query.data})
    await state.set_state(CreateAccount.phone)
    await query.message.answer('Введіть ваш телефон:')
    

