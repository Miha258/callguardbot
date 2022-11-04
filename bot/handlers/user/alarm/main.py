from bot.keyboards.inline import alarm_reasons_markup
from ....database.classes.customer import Customer
from aiogram import types
from aiogram import Router
from aiogram.fsm.context import FSMContext
from .state import AlarmState
from bot.filters.in_black_list import InBlacklist
from bot.filters.user_exist import UserExistFilter
from .callback_query import alarm_router_callbacks
from .commands import alarm_router_commands
from ....misc.utils.cities import get_cities
from bot.misc.bot import bot
from ....misc.utils.alarm import add_new_alarm

alarm_router = Router()
alarm_router.include_router(alarm_router_callbacks)
alarm_router.include_router(alarm_router_commands)


@alarm_router.message(AlarmState.amount_of_guards, InBlacklist(in_blacklist = False), UserExistFilter(user_exist = True))
async def set_amount_of_guards_handler(message: types.Message, state: FSMContext):
    if message.text.isnumeric() and int(message.text) > 0:
        await state.set_data({'amount_of_guards': int(message.text)})
        await state.set_state(AlarmState.explain_reason)
        await message.answer('Поясніть причину виклику охоронців:', reply_markup = alarm_reasons_markup())
    else:
        await message.answer('Невірна кількість охронців, спробуйте ще раз:')


@alarm_router.message(AlarmState.get_user_location)
async def get_alarm_location(message: types.Message, state: FSMContext):
    if message.location:
        user_id = message.from_user.id
        await state.update_data({'location': message.location})

        customer = await Customer.get(user_id)
        data = await state.get_data()
        await state.clear()
        
        if not data:
            await message.answer('Замовлення не дійсне.')
            await message.delete()
        
        elif customer:
            chat_id = get_cities()[customer['city']]
            reason_of_alarm = data["reason_of_alarm"]
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
                text = f'ТРИВОГА\nКількість охоронців: {amount_of_guards}\nПричина: {reason_of_alarm}',
                reply_markup = keyboard_markup
            )
            
            add_new_alarm(alarm_message.message_id, amount_of_guards, user_id)

            keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
                [
                    types.InlineKeyboardButton(text = f"Відмінити виклик", callback_data = "customer_cancle_alarm"),
                ]
            ])
            await message.answer('Ви успішно створили виклик 👍🏻.Використовуйте /alarm_status, щоб побачити статус замовлення', reply_markup = keyboard_markup)
            await message.delete()
    else:
        await message.answer('Ви невірно вказали локацію, спробуйте ще раз:')


