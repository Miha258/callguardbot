from bot import bot
from funcs.account import AccountEdits
from mongodb import Customer, Guards
from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram import F
from config import get_cities
from config import *
from aiogram.methods.edit_message_text import EditMessageText

class AlarmState(StatesGroup):
    amount_of_guards = State()
    explain_reason = State()
    get_user_location = State()
    comfirm_alarm = State()
    user_respond = State()

alarm_router = Router()

@alarm_router.callback_query(F.data == 'alarm')
async def alarm_handler(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(AlarmState.amount_of_guards)
    await query.message.answer('Ви натиснули на кнопку \"Тривога\". Ваші дані та геолокацію буде передано до чату (обране клієнтом місто в особистому кабінеті, або під час реєстрації), вкажіть будь ласка кількість охоронців на виклик (за замовчуванням 1 охоронець):')


@alarm_router.message(AlarmState.amount_of_guards)
async def set_amount_of_guards_handler(message: types.Message, state: FSMContext):
    if message.text.isnumeric():
        await state.set_data({'amount_of_guards': int(message.text)})
        if int(message.text) >= 10:
            await state.set_state(AlarmState.explain_reason)
            await message.answer('Поясність причину виклику великої кількості охоронців:')
        else:
            await state.set_state(AlarmState.get_user_location)
            await message.answer('Тепер скиньте локацію, куди ви викликаєте охоронців:')
    else:
        await message.answer('Невірна кількість охронців, спробуйте ще раз:')


@alarm_router.message(AlarmState.explain_reason)
async def explain_reason_of_alarm_handler(message: types.Message, state: FSMContext):
    await state.update_data({'reason_of_alarm': message.text})
    await state.set_state(AlarmState.get_user_location)
    await message.answer('Тепер скиньте локацію, куди ви викликаєте охоронців:')


@alarm_router.message(AlarmState.get_user_location)
async def get_alarm_location(message: types.Message, state: FSMContext):
    if message.location:
        await state.update_data({'location': message.location})
        await state.set_state(AlarmState.comfirm_alarm)

        keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
            [
                types.InlineKeyboardButton(text = "Підтвердити виклик", callback_data = "comfirm_alarm"),
                types.InlineKeyboardButton(text = "Скасувати виклик", callback_data = "cancle_alarm") 
            ]
        ])
        await message.answer('Ви дійсно бажаєте оформити виклик <b>охорони</b>?', reply_markup = keyboard_markup)
    else:
        await message.answer('Ви невірно вказали локацію, спробуйте ще раз:')
    

@alarm_router.callback_query(AlarmState.comfirm_alarm, F.data.in_({"comfirm_alarm", "cancle_alarm"}))
async def comfirm_alarm_handler(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    user_id = query.from_user.id

    user = await Customer.get(user_id)
    data = await state.get_data()
    await state.clear()

    if answer_data == 'comfirm_alarm':
        chat_id = get_cities()[user['city']]
        reason_of_alarm = data["reason_of_alarm"] if data.get("reason_of_alarm") else ""
        amount_of_guards = data["amount_of_guards"]
        location: types.Location = data["location"]
        
        await bot.send_location(
            chat_id = chat_id, 
            latitude = location.latitude, 
            longitude = location.longitude, 
            horizontal_accuracy = location.horizontal_accuracy,
            live_period = location.live_period,
            heading = location.heading,
            proximity_alert_radius = location.proximity_alert_radius,
        )
        
        keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
            [
                types.InlineKeyboardButton(text = f"Прийняти виклик 0/{amount_of_guards}", callback_data = "take_alarm"),
            ]
        ])
        
        alarm_message = await bot.send_message(
            chat_id = chat_id, 
            text = f'ТРИВОГА\nКількість охоронців: {amount_of_guards}\n{reason_of_alarm}',
            reply_markup = keyboard_markup
        )
        
        add_new_alarm(alarm_message.message_id, amount_of_guards, user_id)
        keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
            [
                types.InlineKeyboardButton(text = f"Відмінити виклик", callback_data = "customer_cancle_alarm"),
            ]
        ])
        await query.message.answer('Ви успішно підтвердили виклик 👍🏻.', reply_markup = keyboard_markup)
        await query.message.delete()
        
    elif answer_data == 'cancle_alarm': 
        await query.message.answer('Ви успішно скасували виклик охорони 👍🏻.')

async def close_alarm(user_id: int, state: FSMContext):
    alarm_id = get_alarm_by_customer_id(user_id)
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
        [
            types.InlineKeyboardButton(text = f"Залишити відгук", callback_data = "leave_respond"),
        ]
    ])
    await state.set_state(AlarmState.user_respond)
    await state.set_data({'guards': get_alarm_guards(alarm_id)})
    await bot.send_message(chat_id = user_id, text = 'Тепер ви можете залишити відгук:', reply_markup = keyboard_markup)
    remove_alarm(alarm_id)

@alarm_router.callback_query(F.data == 'customer_cancle_alarm')
async def comfirm_alarm_handler(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    
    user = await Customer.get(user_id)
    chat_id = get_cities()[user['city']]

    alarm_id = get_alarm_by_customer_id(user_id)
    guards = get_alarm_guards(alarm_id)
    await query.message.answer('Ви успішно завершили виклик охорони 👍🏻.')
    await close_alarm(user_id, state)
 
    await bot.edit_message_reply_markup(chat_id = chat_id, message_id = int(alarm_id), reply_markup = None)
    for guard in guards:
        await bot.send_message(chat_id = guard, text = 'Замовлення завершено замовником')
     
    await query.message.delete()
        

@alarm_router.callback_query(F.data == 'take_alarm')
async def take_alarm_handler(query: types.CallbackQuery):
    message_id = query.message.message_id
    user_id = query.from_user.id
    
    add_guard_to_alarm(message_id, user_id)
    add_to_accepted_alarms(user_id, query.message.message_id)
    current_guards = get_alarm_guards(message_id)
    max_guards = get_max_alarm_guards(message_id)
    
    
    if len(current_guards) == max_guards:
        await query.message.delete_reply_markup()

    # elif await Guards.check_user_exists(user_id) or get_from_accepted_alarms(user_id) is None: 
    await query.message.edit_reply_markup(
        types.InlineKeyboardMarkup(inline_keyboard = [
            [
                types.InlineKeyboardButton(text = f"Прийняти виклик {len(current_guards)}/{max_guards}", callback_data = "take_alarm"),
            ]
        ]
    ))
    
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
        [
            types.InlineKeyboardButton(text = f'Відміна виклику', callback_data = 'cancle_alarm_task'),
            types.InlineKeyboardButton(text = f'Прибув на виклик', callback_data = 'arrived_on_alarm'),
            types.InlineKeyboardButton(text = f'Завершити виклик', callback_data = 'finish_alarm')
        ]
    ])
    customer = await Customer.get(int(get_alarm_customer(message_id)))
    await bot.send_message(chat_id = user_id, text = f'При прибутті на місце виклику\
        нажміть \"Прибув на виклик\"(\"Відміна виклику\" стає недоступною).\
        При завершенні нажміть кнопку \"Завершити виклик\".\n\n     \
        Інформація про клієнта:\n \
        \n<b>ПІБ: {customer["fullname"]}</b>\
        \n<b>Номер телефону: {customer["phone"]}</b>\
        ',
        reply_markup = keyboard_markup)

    
@alarm_router.callback_query(F.data.in_({'cancle_alarm_task', 'arrived_on_alarm', 'finish_alarm'}))
async def guard_alarm_handler(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    alarm_id = int(get_from_accepted_alarms(user_id))
    customer_id = int(get_alarm_customer(alarm_id))


    if query.data == 'cancle_alarm_task':
        await query.message.delete()
        remove_from_accepted_alarms(user_id)
        await query.message.answer('Ви успішно відмінили виклик 👍🏻.')
        
        if get_cont_of_active_guards(alarm_id) == 1:
            close_alarm(customer_id, state)
        else:
            await bot.send_message(chat_id = customer_id, text = 'Один із охорнців відмінив ваш виклик.')
        
        
    elif query.data == 'arrived_on_alarm':
        keyboard_markup = query.message.reply_markup
        del query.message.reply_markup.inline_keyboard[0][0:2]
        
        await query.message.edit_reply_markup(keyboard_markup)
        await query.message.answer('Ви успішно підтвердили своє прибуття 👍🏻.')

    elif query.data == 'finish_alarm':
        remove_from_accepted_alarms(user_id)
        await query.message.delete()
        await query.message.answer('Ви успішно завершили виклик 👍🏻.')
        
        if get_cont_of_active_guards(alarm_id) == 1:
            close_alarm(customer_id, state)
        
        else:
            await bot.send_message(chat_id = customer_id, text = 'Один із охорнців завершив ваш виклик.')