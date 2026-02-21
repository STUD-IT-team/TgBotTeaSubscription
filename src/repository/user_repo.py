from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.abstract_repository.i_user_repo import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user_id: int) -> None:
        print("add", user_id)
        """
        Добавляет нового пользователя в user_table
        """
        query = text("""
            INSERT INTO bot_schema.user_table (tg_id, last_notification_date)
            VALUES (:tg_id, :last_notification_date)
            ON CONFLICT (tg_id) DO NOTHING
        """)
        try:
            row = await self.session.execute(query, {
                "tg_id": user_id,
                "last_notification_date": datetime.utcnow()
            })
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        except SQLAlchemyError:
            await self.session.rollback()
            raise
        return None

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