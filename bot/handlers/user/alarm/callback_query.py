from aiogram import types
from aiogram.fsm.context import FSMContext
from ....misc.utils.cities import get_cities
from ....database.classes.customer import Customer
from ....database.classes.guards import Guards
from ....misc.utils.alarm import *
from .state import AlarmState
from bot.misc.bot import bot
from ....keyboards.inline import account_markup
from aiogram import F
from aiogram import Router
from bot.filters.in_black_list import InBlacklist
from bot.filters.user_exist import UserExistFilter
from ....keyboards.inline import close_alarm

alarm_router_callbacks = Router()


@alarm_router_callbacks.callback_query(F.data == 'alarm', InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))
async def alarm_handler(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(AlarmState.amount_of_guards)
    await query.message.answer('Ви натиснули на кнопку \"Тривога\". Ваші дані та геолокацію буде передано до чату (обране клієнтом місто в особистому кабінеті, або під час реєстрації), вкажіть будь ласка кількість охоронців на виклик (за замовчуванням 1 охоронець):')


@alarm_router_callbacks.callback_query(F.data == 'take_alarm', InBlacklist(in_blacklist = False))
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


@alarm_router_callbacks.callback_query(F.data.in_({"comfirm_alarm", "cancle_alarm"}), UserExistFilter(user_exist = True))
async def comfirm_and_cancle_alarm_handler(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    user_id = query.from_user.id

    customer = await Customer.get(user_id)
    data = await state.get_data()
    await state.clear()

    if not data:
        await query.message.answer('Замовлення не дійсне.')
        await query.message.delete()
    elif customer:
        if answer_data == 'comfirm_alarm':
            chat_id = get_cities()[customer['city']]
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


@alarm_router_callbacks.callback_query(F.data.in_({'cancle_alarm_task', 'arrived_on_alarm', 'finish_alarm'}), InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))
async def guard_alarm_handler(query: types.CallbackQuery):
    user_id = query.from_user.id
    alarm_id = get_from_accepted_alarms(user_id)
    customer_id = int(get_alarm_customer(alarm_id))
    
    if is_alarm_exists(alarm_id):
        if query.data == 'arrived_on_alarm':
            keyboard_markup = query.message.reply_markup
            query.message.reply_markup.inline_keyboard[0].clear()
            keyboard_markup.inline_keyboard[0].append(types.InlineKeyboardButton(text = f'Завершити викдик', callback_data = 'finish_alarm'))

            await query.message.edit_reply_markup(keyboard_markup)
            await query.message.answer('Ви успішно підтвердили своє прибуття 👍🏻.')
            await bot.send_message(customer_id, 'Один із охоронців прибув на місце виклику')

        elif query.data == 'finish_alarm' or query.data == 'cancle_alarm_task':
            await query.message.delete()
            await query.message.answer('Ви успішно завершили виклик 👍🏻.')
            await query.message.answer('Ваш кібінет:', reply_markup = await account_markup(user_id))
            await bot.send_message(customer_id, 'Один із охоронців завершив виклик')
            
            active_guards = get_cont_of_active_guards(alarm_id)
            remove_from_accepted_alarms(user_id)
            
            if active_guards == 1:
                await bot.send_message(chat_id = customer_id, text = 'Виклик завершено охоронцями 👍🏻.')
                await close_alarm(customer_id)
            else:
                await bot.send_message(chat_id = customer_id, text = 'Один із охорнців завершив ваш виклик.')
    else:
        await query.message.reply('Цього виклику не існує.')
        await query.message.delete() 

@alarm_router_callbacks.callback_query(F.data == 'customer_cancle_alarm', InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))
async def customer_cancle_alarm_handler(query: types.CallbackQuery):
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



