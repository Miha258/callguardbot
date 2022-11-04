from aiogram.filters import BaseFilter
from aiogram import types
from ..database.classes.customer import Customer
from ..database.classes.guards import Guards

class UserExistFilter(BaseFilter):
    user_exist: bool

    async def __call__(self, message: types.Message) -> bool:
        user_id = message.from_user.id

        guard_exist = await Guards.check_user_exists(user_id)
        customer = await Customer.check_user_exists(user_id)
        
        if guard_exist or customer:
            if self.user_exist:
                return True
            return False

        elif not self.user_exist:
            return True
        
        else:
            return False