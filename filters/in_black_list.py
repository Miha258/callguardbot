from aiogram.filters import BaseFilter
from aiogram import types
from ..database.classes.blacklist import BlackList


class InBlacklist(BaseFilter):
    in_blacklist: bool

    async def __call__(self, message: types.Message) -> bool:
        return self.in_blacklist == await BlackList.is_in(message.from_user.id)
         
       
        