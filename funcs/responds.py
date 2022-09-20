from mongodb import Customer, UserResponds
from aiogram import types
from validator import *
from aiogram import Router
from aiogram import F
from aiogram.fsm.context import FSMContext


responds_router = Router()

@responds_router.message(F.data == 'leave_respond')
async def choose_registration_type(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    customer = await Customer.get(user_id)

    await state.clear()
    guards = await state.get_data('guards')
    
    for guard in guards:
        await UserResponds.new(guard, customer['fullname'], customer['city'], message.text)

    await message.answer('Відгук залишено👍🏻.')

    