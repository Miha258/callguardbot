from ..main import DB
from abc import ABC


class BaseUser(DB, ABC):
    @classmethod
    async def set_fullname(cls, user_id: int, fullname: str):
        await cls.update(user_id, "set", {"fullname": fullname})

    
    @classmethod
    async def set_city(cls, user_id: int, city: str):
        await cls.update(user_id, "set", {"city": city})
       
        
    @classmethod
    async def set_phone(cls, user_id: int, phone: str):
        await cls.update(user_id, "set", {'phone': phone})
        
    
    @classmethod
    async def check_user_exists(cls, user_id: int) -> bool:
        if await cls.collection.find_one({"_id": user_id}):
            return True
        return False