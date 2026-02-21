from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.abstract_repository.i_transact_repo import ITransactionRepository


class TransactionRepository(ITransactionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def add(self, user_id: int, number: str, date_of_approve: datetime | None = None, admin_id: int | None = None) -> None:
        """
        Добавляет запись в transaction_table
        """
        query = text("""
            INSERT INTO bot_schema.transaction_table (
                user_id, number, date_of_approve, admin_id
            )
            VALUES (:user_id, :number, :date_of_approve, :admin_id)
        """)
        try:
            await self.session.execute(query, {
                "user_id": user_id,
                "number": number,
                "date_of_approve": date_of_approve,
                "admin_id": admin_id
            })
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        except SQLAlchemyError:
            await self.session.rollback()
            raise