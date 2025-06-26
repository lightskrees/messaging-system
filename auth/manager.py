from typing import Optional

from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.base import BaseManager
from src.models import User, UserKey


class UserManager(BaseManager[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_username(self, username: str) -> Optional[User]:
        statement = select(User).where(User.username == username)
        result = await self.session.exec(statement)
        return result.first()

    async def get_user_key(self, user_id: str) -> Optional[UserKey]:
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
