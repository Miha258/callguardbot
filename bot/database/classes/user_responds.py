from ..main import cluster
from ..main import DB


class UserResponds(DB):
    collection = cluster.guardbot.responds

    @classmethod
    async def new(cls, user_id: int, fullname:str, city: str, description: str):
        await cls.insert({"user_id": user_id, "fullname": fullname, "city": city, "description": description})