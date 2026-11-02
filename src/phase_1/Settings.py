from functools import lru_cache
from pathlib import Path
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# The .env lives at the repository root, not next to this file, so we resolve it once.
ENV_FILE_PATH = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    """
    The communication between client and server should always follow this setting.
    """
    appName: str = "phase 1 project"
    # The env file uses SCREAMING_SNAKE_CASE while our fields are camelCase, so each field declares its alias.
    openaiApiKey: str = Field(validation_alias=AliasChoices("OPENAI_API_KEY", "openaiApiKey"))
    openaiModel: str = Field(default="gpt-4.1-mini", validation_alias=AliasChoices("OPENAI_MODEL", "openaiModel"))
    environment: str = "development"
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, env_file_encoding="utf-8", extra="ignore")

@lru_cache
def getSettings() -> Settings:
    return Settings()
