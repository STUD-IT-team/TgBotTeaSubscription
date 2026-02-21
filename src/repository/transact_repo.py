from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from abstract_repository.itransact_repo import ITransactionRepository
from models.transaction import Transaction_Table


class TransactionRepository(ITransactionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def add(self, transaction: Transaction_Table) -> Transaction_Table:
        query = text(f"""
            INSERT INTO bot_schema.transaction_table (user_id, number, date_of_approve, admin_id)
            VALUES (:user_id, :number, :date_of_approve, :admin_id)
            RETURNING id
        """)
        try:
            row = await self.session.execute(query, {
                "user_id": transaction.user_id,
                "number": transaction.number,
                "date_of_approve": transaction.date_of_approve,
                "admin_id": transaction.admin_id
            })
            new_id: int = row.scalar_one()
            await self.session.commit()
            transaction.id = new_id
        except IntegrityError:
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise
        return transaction
