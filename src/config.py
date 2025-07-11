from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    REDIS_URL: str = "redis://localhost:6379/0"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    PRIVATE_KEY_DIR: str
    LOCAL_DB_DIR: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()

INSTALLED_APPS = [
    "src.models.auth",
    "src.models.conversation",
    "src.models.message",
]
