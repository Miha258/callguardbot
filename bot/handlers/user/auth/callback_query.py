from ....database.classes.customer import Customer
from bot.database.classes.guards import Guards
from aiogram import F
from aiogram import Router
from aiogram import types
from .state import CreateAccount
from aiogram.fsm.context import FSMContext
from ....filters.user_exist import UserExistFilter
from ....filters.in_black_list import InBlacklist
from bot.misc.utils.cities import get_cities
from ....keyboards.inline import account_markup
from bot.misc.bot import bot

auth_router_callbacks = Router()


@auth_router_callbacks.callback_query(F.data.in_({'customer', 'guard'}), UserExistFilter(user_exist = False), InBlacklist(in_blacklist = False))
async def choose_registration_type(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data

    if answer_data == 'customer':
        await state.set_data({'user_type': 'customer'})

    elif answer_data == 'guard':
        await state.set_data({'user_type': 'guard'})
    await state.set_state(CreateAccount.fullname)
    await query.message.answer('Введіть ПІБ:')


@auth_router_callbacks.callback_query(CreateAccount.city, F.data.func(lambda data: data in get_cities()))
async def choose_city(query: types.CallbackQuery, state: FSMContext):
    await state.update_data({"city": query.data})
    await state.set_state(CreateAccount.phone)
    await query.message.answer('Введіть ваш телефон:')


@auth_router_callbacks.callback_query(CreateAccount.accept_terms, F.data.func(lambda data: data in {"accept_terms", "refuse_terms"}))
async def choose_city(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    user_id = query.from_user.id

    data = await state.get_data()   
    await state.clear()
    if answer_data == 'accept_terms':
        data['_id'] = user_id
        data['activated'] = False
        user_type = data['user_type']
        del data['user_type']
        
        if user_type == 'guard':
            await Guards.insert(data)
            await query.message.answer('Ви успішно зареєстувалися як <b>охоронець</b>.')

            city_id = get_cities()[data['city']]
            invite = await bot.create_chat_invite_link(city_id)
            await query.message.answer('Тепер вам потрібно зайти в групу охоронців, щоб відсідковувати замовлення:', 
                reply_markup = types.InlineKeyboardMarkup(inline_keyboard = [[
                    types.InlineKeyboardButton(text = "Приєднатися", url = invite.invite_link)
                ]
            ]))
            keyboard_markup = await account_markup(user_id)
            await query.message.answer("Ваш кабінет:", reply_markup = keyboard_markup)
        
        elif user_type == 'customer':
            await Customer.insert(data)
            await query.message.answer('Ви успішно зареєстувалися як <b>клієнт</b>.')
            keyboard_markup = await account_markup(user_id)
            await query.message.answer("Ваш кабінет:", reply_markup = keyboard_markup)
            
    
    elif answer_data == 'refuse_terms':  
        await query.message.answer('Ви відмовлися від реєстрації.')
