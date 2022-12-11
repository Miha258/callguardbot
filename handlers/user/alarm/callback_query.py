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
from bot.filters.is_alarm import AlarmFilter
from ....keyboards.inline import close_alarm

alarm_router_callbacks = Router()


@alarm_router_callbacks.callback_query(F.data == 'alarm', InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))
async def alarm_handler(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(AlarmState.amount_of_guards)
    await query.message.reply('Ви натиснули на кнопку \"Тривога\". Ваші дані та геолокацію буде передано до чату (обране клієнтом місто в особистому кабінеті, або під час реєстрації), вкажіть будь ласка кількість охоронців на виклик (за замовчуванням 1 охоронець):')


@alarm_router_callbacks.callback_query(AlarmState.explain_reason)
async def explain_reason_of_alarm_handler(query: types.CallbackQuery, state: FSMContext):
    reason = query.data
    await state.update_data({'reason_of_alarm': reason})
    await state.set_state(AlarmState.get_user_location)
    await query.message.reply('Тепер скиньте локацію, куди ви викликаєте охоронців:')


@alarm_router_callbacks.callback_query(F.data == 'take_alarm', InBlacklist(in_blacklist = False))
async def take_alarm_handler(query: types.CallbackQuery):
        message_id = query.message.message_id
        user_id = query.from_user.id
    
    # if await Guards.check_user_exists(user_id) and not get_from_accepted_alarms(user_id):
        add_guard_to_alarm(message_id, user_id)
        add_to_accepted_alarms(user_id, query.message.message_id)
        current_guards = get_alarm_guards(message_id)
        max_guards = get_max_alarm_guards(message_id)
        
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
            set_alarm_status(message_id, "Кількість охоронців набрана")
            await query.message.delete_reply_markup()
        
        info_message: types.Message = await bot.send_message(chat_id = user_id, text =  
            f'При прибутті на місце виклику\
            нажміть \"Прибув на виклик\"(\"Відміна виклику\" стає недоступною).\
            При завершенні нажміть кнопку \"Завершити виклик\".\n\n            \
            Інформація про клієнта:\n \
            \n<b>ПІБ: {customer["fullname"]}</b>\
            \n<b>Номер телефону: {customer["phone"]}</b>',
            reply_markup = keyboard_markup)
        await info_message.reply_photo(photo = customer["photo"], caption = 'Фото замовника:')

        alarm_reason = get_alarm_reason(message_id)
        await bot.send_message(chat_id = user_id, text = get_alarm_notation(alarm_reason))
        
        info_message = await bot.send_message(chat_id = customer_chat_id, text = 
            f'Інформація про охоронця:\n\
            \n<b>ПІБ: {guard["fullname"]}</b>\
            \n<b>Номер телефону: {guard["phone"]}</b>\
            \n<b>Місто: {guard["city"]}</b>\
            \n<b>Опис: {guard["description"]}</b>'
        )
        await info_message.reply_photo(photo = guard["photo"], caption = 'Фото охоронця:')


@alarm_router_callbacks.callback_query(F.data.in_({'cancle_alarm_task', 'arrived_on_alarm', 'finish_alarm'}), InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))
async def guard_alarm_handler(query: types.CallbackQuery):
    user_id = query.from_user.id
    alarm_id = get_from_accepted_alarms(user_id)
    customer_id = int(get_alarm_customer(alarm_id))
    max_active_guards = get_max_alarm_guards(alarm_id)
    active_guards = get_count_of_active_guards(alarm_id)
    
    if is_alarm_exists(alarm_id):
        if query.data == 'arrived_on_alarm':
            update_count_of_arrived_guards(alarm_id)

            keyboard_markup = query.message.reply_markup
            query.message.reply_markup.inline_keyboard[0].clear()
            keyboard_markup.inline_keyboard[0].append(types.InlineKeyboardButton(text = f'Завершити виклик', callback_data = 'finish_alarm'))
            
            await query.message.edit_reply_markup(keyboard_markup)
            await query.message.answer('Ви успішно підтвердили своє прибуття 👍🏻.')

            guards_arrived_on_alarm = get_count_of_arrived_guards(alarm_id)
            if guards_arrived_on_alarm == max_active_guards:
                set_alarm_status(alarm_id, "Всі охоронці підтвердили прибуття")
                await bot.send_message(customer_id, 'Всі охоронці прибули на місце виклику')
            else:
                if active_guards == max_active_guards:
                    set_alarm_status(alarm_id, f'{guards_arrived_on_alarm} з {max_active_guards} охоронців прибули на виклик')
                await bot.send_message(customer_id, 'Один із охоронців прибув на місце виклику')


        elif query.data == 'finish_alarm' or query.data == 'cancle_alarm_task':
            await query.message.delete()
            await query.message.answer('Ви успішно завершили виклик 👍🏻.')
            await query.message.answer('Ваш кабінет:', reply_markup = await account_markup(user_id))
            remove_from_accepted_alarms(user_id)

            if active_guards == 0:
                set_alarm_status(alarm_id, "Виклик завершено охоронцями")
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
    await query.message.answer('Ваш кабінет:', reply_markup = await account_markup(user_id))



