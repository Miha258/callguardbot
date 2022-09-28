from aiogram import types
from aiogram import Router
from aiogram.fsm.context import FSMContext
from .state import AlarmState
from ....misc.utils.cities import get_cities
from ....database.classes.customer import Customer
from ....database.classes.guards import Guards
from ....misc.utils.alarm import *
from .state import AlarmState
from bot.misc.bot import bot
from ....keyboards.inline import account_markup
from aiogram import F
from bot.filters.in_black_list import InBlacklist
from bot.filters.user_exist import UserExistFilter


alarm_router = Router()


async def close_alarm(user_id: int):
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
        [
            types.InlineKeyboardButton(text = f"Залишити відгук", callback_data = "leave_respond"),
        ]
    ])
    await bot.send_message(chat_id = user_id, text = 'Тепер ви можете залишити відгук:', reply_markup = keyboard_markup)


@alarm_router.message(AlarmState.amount_of_guards, InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))
async def set_amount_of_guards_handler(message: types.Message, state: FSMContext):
    if message.text.isnumeric() and int(message.text) > 0:
        await state.set_data({'amount_of_guards': int(message.text)})
        if int(message.text) >= 10:
            await state.set_state(AlarmState.explain_reason)
            await message.answer('Поясніть причину виклику великої кількості охоронців:')
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


@alarm_router.callback_query(F.data == 'alarm', InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))
async def alarm_handler(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(AlarmState.amount_of_guards)
    await query.message.answer('Ви натиснули на кнопку \"Тривога\". Ваші дані та геолокацію буде передано до чату (обране клієнтом місто в особистому кабінеті, або під час реєстрації), вкажіть будь ласка кількість охоронців на виклик (за замовчуванням 1 охоронець):')


@alarm_router.callback_query(F.data == 'take_alarm', InBlacklist(in_blacklist = False))
async def take_alarm_handler(query: types.CallbackQuery):
    message_id = query.message.message_id
    user_id = query.from_user.id
    
    add_guard_to_alarm(message_id, user_id)
    add_to_accepted_alarms(user_id, query.message.message_id)
    current_guards = get_alarm_guards(message_id)
    max_guards = get_max_alarm_guards(message_id)
    
    
    # elif await Guards.check_user_exists(user_id) or get_from_accepted_alarms(user_id) is None and not await BlackList.is_in(user_id): 
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
        ]
    ])
    customer = await Customer.get(int(get_alarm_customer(message_id)))
    guard = await Guards.get(user_id)

    customer_chat_id = get_alarm_customer(message_id)
    
    if len(current_guards) >= max_guards:
        await query.message.delete_reply_markup()
    
    await bot.send_message(chat_id = user_id, text = f'При прибутті на місце виклику\
        нажміть \"Прибув на виклик\"(\"Відміна виклику\" стає недоступною).\
        При завершенні нажміть кнопку \"Завершити виклик\".\n\n            \
        Інформація про клієнта:\n \
        \n<b>ПІБ: {customer["fullname"]}</b>\
        \n<b>Номер телефону: {customer["phone"]}</b>',
        reply_markup = keyboard_markup)


    
    await bot.send_message(chat_id = customer_chat_id, text = f'Інформація про охоронця:\n\
        \n<b>ПІБ: {guard["fullname"]}</b>\
        \n<b>Номер телефону: {guard["phone"]}</b>\
        \n<b>Місто: {guard["city"]}</b>\
        \n<b>Опис: {guard["description"]}</b>\
    ')
    

@alarm_router.callback_query(F.data.in_({'cancle_alarm_task', 'arrived_on_alarm', 'finish_alarm'}), InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))
async def guard_alarm_handler(query: types.CallbackQuery):
    user_id = query.from_user.id
    alarm_id = get_from_accepted_alarms(user_id)
    customer_id = int(get_alarm_customer(alarm_id))
    
    if is_alarm_exists(alarm_id):
        if query.data == 'arrived_on_alarm':
            keyboard_markup = query.message.reply_markup
            query.message.reply_markup.inline_keyboard[0].clear()
            keyboard_markup.inline_keyboard[0].append(types.InlineKeyboardButton(text = f'Завершити викдик', callback_data = 'finish_alarm'),)

            await query.message.edit_reply_markup(keyboard_markup)
            await query.message.answer('Ви успішно підтвердили своє прибуття 👍🏻.')

        elif query.data == 'finish_alarm' or query.data == 'cancle_alarm_task':
            await query.message.delete()
            await query.message.answer('Ви успішно завершили виклик 👍🏻.')
            await query.message.answer('Ваш кібінет:', reply_markup = await account_markup(user_id))
            
            active_guards = get_cont_of_active_guards(alarm_id)
            remove_from_accepted_alarms(user_id)
            
            if active_guards == 1:
                await close_alarm(customer_id)
            else:
                await bot.send_message(chat_id = customer_id, text = 'Один із охорнців завершив ваш виклик.')
    else:
        await query.message.reply('Цього виклику не існує.')
        await query.message.delete() 


@alarm_router.callback_query(F.data == 'customer_cancle_alarm', InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))
async def comfirm_alarm_handler(query: types.CallbackQuery):
    user_id = query.from_user.id
    customer = await Customer.get(user_id)
    
    chat_id = get_cities()[customer['city']]
    alarm_id = get_alarm_by_customer_id(user_id)
    guards = get_alarm_guards(alarm_id)
    await query.message.answer('Ви успішно завершили виклик охорони 👍🏻.')
    await close_alarm(user_id)

    await bot.edit_message_reply_markup(chat_id = chat_id, message_id = alarm_id, reply_markup = None)
    for guard in guards:
        await bot.send_message(chat_id = guard, text = 'Замовлення завершено замовником')
    
    await query.message.delete()
    await query.message.answer('Ваш кібінет:', reply_markup = await account_markup(user_id))