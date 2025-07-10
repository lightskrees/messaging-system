import logging
import os

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from ..config import Config as settings
from .main import local_db_metadata

# ToDo: to be implemented soon...


class LocalDBConfig:
    def __init__(self, db_name: str = None):
        if not db_name:
            raise ValueError("Database name must be provided")
        self.engine = None
        self.db_dir = settings.LOCAL_DB_DIR
        self.db_name = db_name

        try:
            self.create_local_engine()
            self.local_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        except Exception as e:
            logging.error(f"Failed to initialize local database: {str(e)}")
            raise

    async def init_db(self):
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(local_db_metadata.create_all)
        except SQLAlchemyError as e:
            logging.error(f"Failed to initialize database tables: {str(e)}")
            raise

    def get_db(self) -> str:
        try:
            user_local_db = os.path.join(self.db_dir, self.db_name)
            os.makedirs(user_local_db, exist_ok=True)
            db_path = os.path.join(user_local_db, "msg_store.db")
            return f"sqlite+aiosqlite:///{db_path}"
        except OSError as e:
            logging.error(f"Failed to create database directory: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error creating database path: {str(e)}")
            raise

    def create_local_engine(self):
        try:
            self.engine = AsyncEngine(create_engine(self.get_db(), echo=True))
        except Exception as e:
            logging.error(f"Failed to create database engine: {str(e)}")
            raise

    async def create_db_tables(self):
        try:
            async with self.engine.connect() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
        except SQLAlchemyError as e:
            logging.error(f"Failed to create database tables: {str(e)}")
            raise
