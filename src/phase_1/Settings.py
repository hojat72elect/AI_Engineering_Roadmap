from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    The communication between client and server should always follow this setting.
    """
    appName = "phase 1 project"
    environment = "development"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache
def getSettings() -> Settings:
    return Settings()
