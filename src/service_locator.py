import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from dataclasses import dataclass 
from typing import Any

_async_session_maker = None

from abstract_repository.i_user_repo import IUserRepository
from abstract_repository.i_transact_repo import ITransactionRepository

from repository.user_repo import UserRepository
from repository.transact_repo import TransactionRepository
from settings import settings

@dataclass
class Repositories:
    def __init__(
        self,
        transaction_repo: ITransactionRepository,
        user_repo: IUserRepository,
    ):
        self.transaction_repo = transaction_repo
        self.user_repo = user_repo


async def get_sessionmaker(max_retries: int = 5, delay: int = 2) -> Any:
    global _async_session_maker
    if _async_session_maker is not None:
        return _async_session_maker
    engine = create_async_engine(
        settings.DATABASE_URL_ASYNC,
        connect_args={"server_settings": {"search_path": "bot_schema"}},
        echo=True,
        pool_pre_ping=True,
    )
    for attempt in range(max_retries):
        try:
            _async_session_maker = sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )  # type: ignore
            return _async_session_maker
        except OperationalError as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Повторная попытка подключения через {delay} секунд...")
                await asyncio.sleep(delay)
            else:
                raise RuntimeError(
                    "Не удалось подключиться к базе данных после нескольких попыток."
                )
    return None


async def get_repositories():
    global _async_session_maker

    if _async_session_maker is None:
        _async_session_maker = await get_sessionmaker()
    async with _async_session_maker() as session:
        user_repo: IUserRepository = UserRepository(session)
        transaction_repo: ITransactionRepository = TransactionRepository(session)

        repositories = Repositories(transaction_repo, user_repo)

    return repositories
