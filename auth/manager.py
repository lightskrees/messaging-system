import uuid
from typing import Optional, Union

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.base import BaseManager
from src.db_config import SessionDep
from src.models import User, UserKey


class UserManager(BaseManager[User]):
    def __init__(self, sessions: SessionDep):
        super().__init__(sessions, User)

    async def get_by_username(self, username: str, using_local_db: bool = False) -> Optional[User]:
        statement = select(User).where(User.username == username)

        session = self.local_session if using_local_db else self.session
        result = await session.exec(statement)
        return result.first()

    async def get_user_key(self, user_id: Union[str, uuid.UUID]) -> Optional[UserKey]:
        statement = select(UserKey).where(UserKey.user_id == user_id)
        result = await self.session.exec(statement)
        return result.first()

    async def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        result = await self.session.exec(statement)
        return result.first()

    async def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        statement = select(User).where(User.phone_number == phone_number)
        result = self.session.exec(statement)
        return result.first()
