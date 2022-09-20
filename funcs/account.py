from config import get_cities
from mongodb import Customer, Guards
from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram import F

account_router = Router()

class AccountEdits(StatesGroup):
    fullname = State()
    city = State()
    description = State()
    accept_city_change = State()
    accept_delete_account = State()


async def get_user_account_markup(user_id: int) -> types.InlineKeyboardMarkup | None:
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
            [
                types.InlineKeyboardButton(text = "Редагування", callback_data = "edit_account"),
                types.InlineKeyboardButton(text = "Видалити акаунт", callback_data = "delete_account")
            ]
        ]
    )
    if await Customer.check_user_exists(user_id):
        keyboard_markup.inline_keyboard[0].append(types.InlineKeyboardButton(text = "Тривога", callback_data = "alarm"))
    
    return keyboard_markup

@account_router.callback_query(F.data.in_({'edit_account', 'delete_account'}))
async def user_account_options(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    user_id = query.from_user.id
    user = await Customer.get(user_id) or await Guards.get(user_id)
    
    if answer_data == 'edit_account':
        keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
                [
                    types.InlineKeyboardButton(text = "ПІБ", callback_data = "fullname"),
                    types.InlineKeyboardButton(text = "Місто", callback_data = "city"),
                ]
            ]
        )
        
        if await Guards.check_user_exists(user_id):
            keyboard_markup.inline_keyboard[0].append(types.InlineKeyboardButton(text = "Опис", callback_data = "description"))
        

        user_data = f'\nПІБ: {user["fullname"]}' + f'\nМісто: {user["city"]}' + f'\nТелефон: {user["phone"]}' + f'\nОпис: {user["description"]}' if user.get('description') else ''
        await query.message.edit_text('Виберіть дані, які хочите змінити:' + user_data, reply_markup = keyboard_markup)

    elif answer_data == 'delete_account':
        await state.set_state(AccountEdits.accept_delete_account)
        keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
                [
                    types.InlineKeyboardButton(text = "Видалити", callback_data = "Yes"),
                    types.InlineKeyboardButton(text = "Відмінити", callback_data = "No")
                ]
            ]
        )
        await query.message.answer(f"Ви дійсно бажаєте видалити аккаунт, усі дані будуть видалені", reply_markup = keyboard_markup)
        

@account_router.callback_query(F.data.in_({'fullname', 'city', 'description'}))
async def edit_account_options(query: types.CallbackQuery, state: FSMContext):
    await query.message.delete()
    answer_data = query.data
    user_id = query.from_user.id
    

    if answer_data == 'fullname':
        await query.message.answer("Введіть новий ПІБ:")
        await state.set_state(AccountEdits.fullname)
        
    elif answer_data == 'city':
        await state.set_state(AccountEdits.accept_city_change)
        current_city = None

        if await Guards.check_user_exists(user_id):
            current_city = await Guards.get(user_id)
        elif await Customer.check_user_exists(user_id):
            current_city = await Customer.get(user_id)

        keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
                [
                    types.InlineKeyboardButton(text = "Так", callback_data = "Yes"),
                    types.InlineKeyboardButton(text = "Ні", callback_data = "No")
                ]
            ]
        )
        await query.message.answer(f"Ви точно хочете змінити місто? Ваше місто: {current_city['city']}", reply_markup = keyboard_markup)
 
    elif answer_data == 'description':
        await state.set_state(AccountEdits.description)
        await query.message.answer("Введіть новий опис:")


@account_router.message(AccountEdits.fullname)
async def change_user_fullname_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if await Guards.check_user_exists(user_id):
        await Guards.set_fullname(user_id, message.text)
    elif await Customer.check_user_exists(user_id):
        await Customer.set_fullname(user_id, message.text)

    await message.answer("Ви успішно змінили ПІБ 👍🏻.")
    await state.clear()
    await message.answer("Ваш кабінет: ", reply_markup = await get_user_account_markup(user_id))


@account_router.message(AccountEdits.city)
async def change_user_city_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if await Guards.check_user_exists(user_id):
        await Guards.set_city(user_id, message.text)
    elif await Customer.check_user_exists(user_id):
        await Customer.set_city(user_id, message.text)

    await message.answer("Місто успішно змінене 👍🏻.") 
    await state.clear()
    await message.answer("Ваш кабінет: ", reply_markup = await get_user_account_markup(user_id))


@account_router.message(AccountEdits.description)
async def change_user_description_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if await Guards.check_user_exists(user_id):
        await Guards.set_description(user_id, message.text)

    await message.answer("Ви успішно змінили опис 👍🏻.")
    await state.clear()
    await message.answer("Ваш кабінет: ", reply_markup = await get_user_account_markup(user_id))
    

@account_router.callback_query(AccountEdits.accept_city_change, F.data.in_({'Yes', 'No'}))
async def comfirm_city_change(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    user_id = query.from_user.id
    
    if answer_data == 'Yes':
        await state.set_state(AccountEdits.city)  
        await query.message.answer(f"Виберіть нове місто із списку ({' ,'.join(get_cities().keys())}): ")
        await query.message.delete()

    elif answer_data == 'No':
        await query.message.edit_text('Ваш кабінет:', reply_markup = await get_user_account_markup(user_id))


@account_router.callback_query(AccountEdits.accept_delete_account, F.data.in_({'Yes', 'No'}))
async def comfirm_account_delate(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    user_id = query.from_user.id

    await state.clear()
    await query.message.delete()

    if answer_data == 'Yes':
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
    
    elif answer_data == 'No':
        await query.message.edit_text('Ваш кабінет:', reply_markup = await get_user_account_markup(user_id))
    