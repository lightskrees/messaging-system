from abc import ABC
from typing import Generic, List, Optional, Type, TypeVar

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db_config import SessionDep

T = TypeVar("T", bound="SQLModel")

# ToDo: the local storage sync with with SQLite to be implemented soon...


class BaseManager(Generic[T], ABC):
    def __init__(self, sessions: SessionDep, model: Type[T]):
        self.session = sessions.main_session
        self.local_session = sessions.local_session
        self.model = model

    async def create(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)

        # self.sqlite_session.add(obj)
        # await self.sqlite_session.commit()
        # await self.sqlite_session.refresh(obj)
        return obj

    async def get_by_id(self, id: str, use_local_db: bool = False) -> Optional[T]:

        # session = self.sqlite_session if use_local_db else self.session
        return await self.session.get(self.model, id)

    async def get_all(self) -> List[T]:
        statement = select(self.model)
        result = await self.session.exec(statement)
        return result.all()

    async def update(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)

        # self.sqlite_session.add(obj)
        # await self.sqlite_session.commit()
        # await self.sqlite_session.refresh(obj)

        return obj

    async def delete(self, id: str) -> bool:
        obj = await self.get_by_id(id)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()

            # await self.sqlite_session.delete(obj)
            # await self.sqlite_session.commit()

            return True
        return False
