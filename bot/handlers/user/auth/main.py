from aiogram import types
from aiogram import Router
from aiogram.fsm.context import FSMContext
from .state import CreateAccount
from ....database.classes.customer import Customer
from ....database.classes.guards import Guards
from ....keyboards.inline import account_markup
from ....keyboards.inline import get_cities_markup
from bot.misc.bot import bot
from bot.misc.utils.cities import get_cities
from ....filters.user_exist import UserExistFilter
from ....filters.is_phone import ValidtePhone

from .commands import auth_router_commands
from .callback_query import auth_router_callbacks

auth_router = Router()
auth_router.include_router(auth_router_commands)
auth_router.include_router(auth_router_callbacks)


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
    invite_link = await bot.create_chat_invite_link(city_id)
    await message.answer('Тепер вам потрібно зайти в групу охоронців, щоб відсідковувати замовлення:', 
        reply_markup = types.InlineKeyboardMarkup(inline_keyboard = [[
            types.InlineKeyboardButton(text = "Приєднатися", url = invite_link)
        ]
    ]
    ),)

    keyboard_markup = await account_markup(user_id)
    await message.answer("Ваш кабінет:", reply_markup = keyboard_markup)
    

