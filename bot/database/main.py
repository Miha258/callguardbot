from typing import Any
import motor.motor_asyncio 
from abc import ABC
from os import environ


MONGODB_URI = "localhost:27017"
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