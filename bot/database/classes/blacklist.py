from ..main import cluster
from ..main import DB



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