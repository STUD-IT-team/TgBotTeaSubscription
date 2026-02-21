from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.user import User_Table


class IUserRepository(ABC):
    @abstractmethod
    async def add(self, user: User_Table) -> User_Table:
        pass
    
    async def update(self, tg_id:int, last_notification_date: datetime) -> User_Table:
        pass