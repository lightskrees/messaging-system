import os
from dataclasses import dataclass
from typing import Annotated

from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import Config as settings

# ToDo: logic about two sessions to be configured soon...


def get_db_path() -> str:
    os.makedirs(settings.LOCAL_DB_DIR, exist_ok=True)
    return os.path.join(settings.LOCAL_DB_DIR, "msg_store.db")


def get_db_url() -> str:
    return f"sqlite+aiosqlite:///{get_db_path()}"


main_engine = AsyncEngine(create_engine(settings.DATABASE_URL, echo=False))
local_async_engine = AsyncEngine(create_engine(get_db_url(), echo=True))


async def init_db():
    async with local_async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@dataclass
class DatabaseSessions:
    main_session: AsyncSession
    local_session: AsyncSession


async def get_sessions():
    session = sessionmaker(bind=main_engine, class_=AsyncSession, expire_on_commit=False)

    local_session = sessionmaker(bind=local_async_engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as session, local_session() as local_session:
        yield DatabaseSessions(session, local_session)


# SessionDep = Annotated[Session, Depends(get_sessions)]
SessionDep = DatabaseSessions
