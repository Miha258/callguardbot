from config import MONGODB_URI
from typing import Any
import motor.motor_asyncio 
from abc import ABC


cluster: motor.motor_asyncio.core.AgnosticClient = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)

class DB(ABC):
    collection: motor.motor_asyncio.core.AgnosticCollection 


    def __init__(self, _id):
        self._id = _id
    

    @classmethod
    async def get(cls, user_id: int) -> dict[str, Any] | None:
        user = await cls.collection.find_one({"_id": user_id})
        if user:
           return user
        return None


    @classmethod
    async def update(cls, user_id: int, flag: str, query: dict[str, Any]) -> bool:
        cls.collection.update_one({"_id": user_id}, {f'${flag}': query})
    
    
    @classmethod
    async def insert(cls, query: dict[str, Any]):
        await cls.collection.insert_one(query)


    @classmethod
    async def delete(cls, user_id: str):
        await cls.collection.delete_one({"_id": user_id})


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

class Customer(BaseUser):
    collection = cluster.guardbot.customers

    @classmethod
    async def set_activated(cls, user_id: int, toggle: bool) -> bool:
        await cls.update(user_id, "set", {'activated': toggle})


class Guards(BaseUser):
    collection = cluster.guardbot.guards

            
    @classmethod
    async def set_description(cls, user_id: int, description: str):
        await cls.update(user_id, "set", {"description": description})

class UserResponds(DB):
    collection = cluster.guardbot.responds

    @classmethod
    async def new(cls, user_id: int, fullname:str, city: str, description: str):
        await cls.insert({"user_id": user_id, "fullname": fullname, "city": city, "description": description})

class BlackList(DB):
    collection = cluster.guardbot.blacklist

    @classmethod
    async def is_in(cls, user_id) -> bool:
        return bool(await cls.get(user_id))
    
    @classmethod
    async def add(cls, user_id: int):
        await cls.insert({"user_id": user_id})

    @classmethod
    async def remove(cls, user_id: int):
        await cls.delete(user_id)


