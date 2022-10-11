from aiogram import types
from aiogram import Router
from aiogram import F
from aiogram.fsm.context import FSMContext
from .state import QuestinerState
from ....misc.utils.alarm import *
from ....filters.user_exist import UserExistFilter


questioner_router = Router()

@questioner_router.message(QuestinerState.questioner, UserExistFilter(user_exist = True))
async def questioner_handler(message: types.Message, state: FSMContext):
    await state.clear()