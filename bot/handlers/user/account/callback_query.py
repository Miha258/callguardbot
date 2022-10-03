from aiogram import types
from aiogram import Router
from aiogram import F
from aiogram.fsm.context import FSMContext
from bot.filters.user_exist import UserExistFilter
from bot.misc.bot import bot
from ....keyboards.inline import account_markup, get_cities_markup
from ....database.classes.customer import Customer
from ....database.classes.guards import Guards
from .state import AccountEdits
from bot.misc.utils.cities import get_cities

account_router_callbacks = Router()


@account_router_callbacks.callback_query(F.data.in_({'edit_account', 'delete_account'}), UserExistFilter(user_exist = True))
async def user_account_options(query: types.CallbackQuery):
    answer_data = query.data
    user_id = query.from_user.id
    user = await Customer.get(user_id) or await Guards.get(user_id)

    if answer_data == 'edit_account':
        keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
                [
                    types.InlineKeyboardButton(text = "ПІБ", callback_data = "edit_fullname"),
                    types.InlineKeyboardButton(text = "Місто", callback_data = "edit_city"),
                    types.InlineKeyboardButton(text = "Фото", callback_data = "edit_photo"),
                ]
            ]
        )
        
        if await Guards.check_user_exists(user_id):
            keyboard_markup.inline_keyboard[0].append(types.InlineKeyboardButton(text = "Опис", callback_data = "edit_description"))
        

        guard_description = f'\nОпис: {user["description"]}' if user.get('description') else ''
        user_data = f'\nПІБ: {user["fullname"]}' + f'\nМісто: {user["city"]}' + f'\nТелефон: {user["phone"]}' + guard_description
        user_photo = user["photo"]

        await query.message.edit_text('Виберіть дані, які хочите змінити:' + user_data, reply_markup = keyboard_markup)
        await query.message.reply_photo(user_photo, 'Ваше фото')

    elif answer_data == 'delete_account':
        keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
                [
                    types.InlineKeyboardButton(text = "Видалити", callback_data = "accept_account_deleting"),
                    types.InlineKeyboardButton(text = "Відмінити", callback_data = "cancle_account_deleting")
                ]
            ]
        )
        await query.message.answer(f"Ви дійсно бажаєте видалити аккаунт, усі дані будуть видалені", reply_markup = keyboard_markup)
    

@account_router_callbacks.callback_query(F.data.in_({'edit_fullname', 'edit_city', 'edit_description', 'edit_photo'}), UserExistFilter(user_exist = True))
async def edit_account_options(query: types.CallbackQuery, state: FSMContext):
    await query.message.delete()
    answer_data = query.data
    user_id = query.from_user.id
 
    if answer_data == 'edit_fullname':
        await query.message.answer("Введіть новий ПІБ:")
        await state.set_state(AccountEdits.fullname)
        
    elif answer_data == 'edit_city':
        current_city = None
    
        if await Guards.check_user_exists(user_id):
            current_city = await Guards.get(user_id)
        elif await Customer.check_user_exists(user_id):
            current_city = await Customer.get(user_id)

        keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
                [
                    types.InlineKeyboardButton(text = "Так", callback_data = "accept_city_changing"),
                    types.InlineKeyboardButton(text = "Ні", callback_data = "cancle_city_changing")
                ]
            ]
        )
        await query.message.answer(f"Ви точно хочете змінити місто? Ваше місто: {current_city['city']}", reply_markup = keyboard_markup)

    elif answer_data == 'edit_photo':
        await state.set_state(AccountEdits.photo)
        await query.message.answer("Скиньте нове фото:")

    elif answer_data == 'edit_description':
        await state.set_state(AccountEdits.description)
        await query.message.answer("Введіть новий опис:")


@account_router_callbacks.callback_query(AccountEdits.city, F.data.in_(get_cities()), UserExistFilter(user_exist = True))
async def change_user_city_handler(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.delete()
    await state.clear()
    
    city_id = None
    
    if await Guards.check_user_exists(user_id):
        guard = await Guards.get(user_id)
        city_id = get_cities()[guard['city']]
        await Guards.set_city(user_id, query.data)

        if await bot.get_chat_member(city_id, user_id):
            await bot.kick_chat_member(city_id, user_id)
    
    elif await Customer.check_user_exists(user_id):
        customer = await Customer.get(user_id)
        city_id = get_cities()[customer['city']]
        await Customer.set_city(user_id, query.data) 
    
        city_id = get_cities()[query.data]
        invite_invite = await bot.create_chat_invite_link(city_id)
        await query.message.answer('Тепер вам потрібно зайти в групу охоронців, щоб відсідковувати замовлення:', 
            reply_markup = types.InlineKeyboardMarkup(inline_keyboard = [[
                types.InlineKeyboardButton(text = "Приєднатися", url = invite_invite.invite_link)
            ]
        ]   
    ))
    await query.message.answer("Місто успішно змінене 👍🏻.")
    await query.message.answer("Ваш кабінет: ", reply_markup = await account_markup(user_id))


@account_router_callbacks.callback_query(F.data.in_({"accept_city_changing", "cancle_city_changing"}), UserExistFilter(user_exist = True))
async def comfirm_city_change(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    user_id = query.from_user.id
    
    
    if answer_data == 'accept_city_changing':
        await state.set_state(AccountEdits.city)
        keyboard_markup = get_cities_markup()
        await query.message.answer("Виберіть нове місто із списку:", reply_markup = keyboard_markup)
        await query.message.delete()

    elif answer_data == 'cancle_city_changing':
        await query.message.edit_text('Ваш кабінет:', reply_markup = await account_markup(user_id))


@account_router_callbacks.callback_query(F.data.in_({"cancle_account_deleting", "accept_account_deleting"}), UserExistFilter(user_exist = True))
async def comfirm_account_delate(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    user_id = query.from_user.id

    await state.clear()
    await query.message.delete()

    if not await Customer.check_user_exists(user_id) and not await Guards.check_user_exists(user_id):
        await query.message.answer("Ви не зареєстровані!")
    else:
        if answer_data == 'accept_account_deleting':
            if await Customer.check_user_exists(user_id):
                await Customer.delete(user_id)
            elif await Guards.check_user_exists(user_id):
                await Guards.delete(user_id)

            await query.message.answer('Ваш акаунт видалено 👍🏻.')
            keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
                [
                    types.InlineKeyboardButton(text = "Клієнт", callback_data = "customer"),
                    types.InlineKeyboardButton(text = "Охоронець", callback_data = "guard") 
                ]
            ])
            
            await query.message.answer("Вас вітає <b>Guard bot</b>.Зареєструйтесь в системі як:", reply_markup = keyboard_markup)
        
        elif answer_data == 'cancle_account_deleting':
            await query.message.edit_text('Ваш кабінет:', reply_markup = await account_markup(user_id))