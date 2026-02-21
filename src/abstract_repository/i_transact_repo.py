from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.transaction import Transaction_Table


class ITransactionRepository(ABC):
    @abstractmethod
    async def add(self, transact: Transaction_Table) -> Transaction_Table:
        pass