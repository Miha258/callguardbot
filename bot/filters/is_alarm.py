from bot.misc.utils.alarm import get_from_accepted_alarms
from aiogram import types
from aiogram.filters import BaseFilter
from ..database.classes.guards import Guards
from ..database.classes.blacklist import BlackList


class AlarmFilter(BaseFilter):
    is_alarm: bool

    async def __call__(self, message: types.Message) -> bool:
        if self.is_alarm:
            user_id = message.from_user.id
            return await Guards.check_user_exists(user_id) or get_from_accepted_alarms(user_id) is None and not await BlackList.is_in(user_id)

