from aiogram import Router
from aiogram import types
from ....database.classes.customer import Customer
from ....database.classes.guards import Guards
from aiogram.fsm.context import FSMContext
from .state import AccountEdits
from ....misc.utils.cities import *
from ....keyboards.inline import *
from .callback_query import account_router_callbacks
from bot.filters.user_exist import UserExistFilter

account_router = Router()
account_router.include_router(account_router_callbacks)


@account_router.message(AccountEdits.fullname, UserExistFilter(user_exist = True))
async def change_user_fullname_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if await Guards.check_user_exists(user_id):
        await Guards.set_fullname(user_id, message.text)
    elif await Customer.check_user_exists(user_id):
        await Customer.set_fullname(user_id, message.text)

    await message.answer("Ви успішно змінили ПІБ 👍🏻.")
    await state.clear()
    await message.answer("Ваш кабінет: ", reply_markup = await account_markup(user_id))


@account_router.message(AccountEdits.photo, UserExistFilter(user_exist = True))
async def change_user_description_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.photo:
        if await Guards.check_user_exists(user_id):
            await Guards.set_photo(user_id, message.photo[0].file_id)
        elif await Customer.check_user_exists(user_id):
            await Customer.set_photo(user_id, message.photo[0].file_id )

        await message.answer("Ви успішно змінили фото 👍🏻.")
        await state.clear()
        await message.answer("Ваш кабінет:", reply_markup = await account_markup(user_id))
    else:
        await message.answer('Скиньте ваше фото ще раз')


@account_router.message(AccountEdits.description, UserExistFilter(user_exist = True))
async def change_user_description_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await Guards.set_description(user_id, message.text)
    await message.answer("Ви успішно змінили опис 👍🏻.")
    await state.clear()
    await message.answer("Ваш кабінет: ", reply_markup = await account_markup(user_id))



    