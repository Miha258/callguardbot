from aiogram.filters import BaseFilter
from aiogram import types
from ..misc.utils.admin import admin_exists


class AdminFilter(BaseFilter):
    is_admin: bool

    async def __call__(self, message: types.Message) -> bool:
        return self.is_admin == admin_exists(message.from_user.id)