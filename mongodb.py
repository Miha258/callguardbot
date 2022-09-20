import asyncio
from typing import Any
import motor.motor_asyncio 
from abc import ABC


conn_addres = "mongodb+srv://tEST:Hrfb2kLK8Aoo4Fxk@cluster0.zlpox.mongodb.net/guardbot?retryWrites=true&w=majority"
cluster: motor.motor_asyncio.core.AgnosticClient = motor.motor_asyncio.AsyncIOMotorClient(conn_addres)

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
    async def insert(self, query: dict[str, Any]):
        await self.collection.insert_one(query)


    @classmethod
    async def delete(self, user_id: str):
        await self.collection.delete_one({"_id": user_id})


class BaseUser(DB, ABC):
    @classmethod
    async def set_fullname(self, user_id: int, fullname: str):
        await self.update(user_id, "set", {"fullname": fullname})


    @classmethod
    async def set_city(self, user_id: int, city: str):
        await self.update(user_id, "set", {"city": city})
       
        
    @classmethod
    async def set_phone(self, user_id: int, phone: str):
        await self.update(user_id, "set", {'phone': phone})
        
    
    @classmethod
    async def check_user_exists(cls, user_id: int) -> bool:
        if await cls.collection.find_one({"_id": user_id}):
            return True
        return False

class Customer(BaseUser):
    collection = cluster.guardbot.customers


class Guards(BaseUser):
    collection = cluster.guardbot.guards

            
    @classmethod
    async def set_description(self, user_id: int, description: str):
        await self.update(user_id, "set", {"description": description})

class UserResponds(DB):
    collection = cluster.guardbot.responds

    @classmethod
    async def new(self, user_id: int, fullname:str, city: str, description: str):
        await self.insert({"user_id": user_id, "fullname": fullname, "city": city, "description": description})

