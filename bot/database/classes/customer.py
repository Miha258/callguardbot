from ..main import cluster
from .baseuser import BaseUser


class Customer(BaseUser):
    collection = cluster.guardbot.customers

    @classmethod
    async def set_activated(cls, user_id: int, toggle: bool) -> bool:
        await cls.update(user_id, "set", {'activated': toggle})
