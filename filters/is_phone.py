from aiogram.filters import BaseFilter
from aiogram import types


class ValidtePhone(BaseFilter):
    is_phone: bool

    async def __call__(self, message: types.Message) -> bool:
        if self.is_phone:
            phone = message.text

            if phone.replace('+', '').isnumeric() and len(phone) == 13 and phone.startswith('+380'):
                return True
            else:
                await message.answer('Невірний номер, спробуйие ще раз:')
                return False
        else:
            return False 