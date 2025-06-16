from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import Config as settings

async_engine = AsyncEngine(create_engine(settings.DATABASE_URL, echo=True))


async def create_db_tables():
    async with async_engine.connect() as conn:
        await conn.run_sync(SQLModel.metadate.create_all)


async def get_session():
    session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
