from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Generic, TypeVar, Type, Optional, List
from abc import ABC, abstractmethod

T = TypeVar('T', bound="SQLModel")

class BaseManager(Generic[T], ABC):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def create(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, id: str) -> Optional[T]:
        return await self.session.get(self.model, id)

    async def get_all(self) -> List[T]:
        statement = select(self.model)
        result = await self.session.exec(statement)
        return result.all()

    async def update(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: str) -> bool:
        obj = await self.get_by_id(id)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
            return True
        return False