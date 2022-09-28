from ..main import cluster
from .baseuser import BaseUser


class Guards(BaseUser):
    collection = cluster.guardbot.guards

    @classmethod
    async def set_description(cls, user_id: int, description: str):
        await cls.update(user_id, "set", {"description": description})