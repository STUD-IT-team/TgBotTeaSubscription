from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class IUserRepository(ABC):
    @abstractmethod
    async def add(self, user_id: int) -> None:
        pass
    
    async def update(self, tg_id:int, last_notification_date: datetime) -> User_Table:
        pass