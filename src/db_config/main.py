import os
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import Config as settings

# ToDo: logic about two sessions to be configured soon...


def get_db_path() -> str:
    os.makedirs(settings.LOCAL_DB_DIR, exist_ok=True)
    return os.path.join(settings.LOCAL_DB_DIR, "msg_store.db")


# def get_db_url() -> str:
#     return f"sqlite+aiosqlite:///{get_db_path()}"

main_engine = AsyncEngine(create_engine(settings.DATABASE_URL, echo=True))
# local_async_engine = AsyncEngine(create_engine(get_db_url(), echo=True))


async def get_session():
    session = sessionmaker(bind=main_engine, class_=AsyncSession, expire_on_commit=False)

    # sqlite_session = sessionmaker(bind=local_async_engine, class_=AsyncSession, expire_on_commit=False)

    async with (
        session() as session,
        # sqlite_session() as sqlite_session
    ):
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
