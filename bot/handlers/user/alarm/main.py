from aiogram import types
from aiogram import Router
from aiogram.fsm.context import FSMContext
from .state import AlarmState
from bot.filters.in_black_list import InBlacklist
from bot.filters.user_exist import UserExistFilter
from .callback_query import alarm_router_callbacks
from .commands import alarm_router_commands

alarm_router = Router()
alarm_router.include_router(alarm_router_callbacks)
alarm_router.include_router(alarm_router_commands)


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


