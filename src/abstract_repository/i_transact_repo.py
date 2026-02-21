from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class ITransactionRepository(ABC):
    @abstractmethod
    async def add(self, user_id: int, number: str, date_of_approve: datetime | None = None, admin_id: int | None = None) -> None:
        pass