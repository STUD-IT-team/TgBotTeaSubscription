from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from abstract_repository.iuser_repo import IUserRepository
from models.user import User_Table


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user: User_Table) -> User_Table:
        """
        Добавляет нового пользователя в user_table
        """
        query = text("""
            INSERT INTO bot_schema.user_table (tg_id, last_notification_date)
            VALUES (:tg_id, :last_notification_date)
            RETURNING id
        """)
        try:
            row = await self.session.execute(query, {
                "tg_id": user.tg_id,
                "last_notification_date": user.last_notification_date
            })
            new_id: int = row.scalar_one()
            await self.session.commit()
            user.id = new_id
        except IntegrityError:
            await self.session.rollback()
            raise
        except SQLAlchemyError:
            await self.session.rollback()
            raise
        return user

    async def update_last_notification(self, tg_id: int, last_notification_date: datetime) -> None:
        """
        Обновляет last_notification_date пользователя по tg_id
        """
        query = text("""
            UPDATE bot_schema.user_table
            SET last_notification_date = :last_notification_date
            WHERE tg_id = :tg_id
        """)
        try:
            await self.session.execute(query, {
                "tg_id": tg_id,
                "last_notification_date": last_notification_date
            })
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise