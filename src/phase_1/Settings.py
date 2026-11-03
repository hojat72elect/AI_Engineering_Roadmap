from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The .env lives at the repository root, not next to this file, so we resolve it once.
ENV_FILE_PATH = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    """
    The communication between client and server should always follow this setting.
    """
    appName: str = "phase 1 project"

    # Which provider answers the questions. Changing this single value re-points the whole stack.
    llmProvider: Literal["openai", "gemini"] = Field(
        default="openai", validation_alias=AliasChoices("LLM_PROVIDER", "llmProvider")
    )

    # The env file uses SCREAMING_SNAKE_CASE while our fields are camelCase, so each field declares its alias.
    openaiApiKey: str | None = Field(default=None, validation_alias=AliasChoices("OPENAI_API_KEY", "openaiApiKey"))
    openaiModel: str = Field(default="gpt-4.1-mini", validation_alias=AliasChoices("OPENAI_MODEL", "openaiModel"))

    geminiApiKey: str | None = Field(default=None, validation_alias=AliasChoices("GEMINI_API_KEY", "geminiApiKey"))
    # Google retires pinned model names, and a retired name answers 404 instead of answering questions,
    # so the default is the alias that always points at the current flash model.
    geminiModel: str = Field(default="gemini-flash-latest", validation_alias=AliasChoices("GEMINI_MODEL", "geminiModel"))

    # The SDK retries connection errors and 5xx responses with exponential backoff; this is how many times.
    llmMaxRetries: int = Field(default=2, validation_alias=AliasChoices("LLM_MAX_RETRIES", "llmMaxRetries"))

    environment: str = "development"
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, env_file_encoding="utf-8", extra="ignore")

    @property
    def providerApiKey(self) -> str:
        """
        The credential of whichever provider `llmProvider` selects.
        """
        apiKey = self.geminiApiKey if self.llmProvider == "gemini" else self.openaiApiKey

        if not apiKey:
            raise ValueError(f"LLM_PROVIDER is '{self.llmProvider}' but its API key is missing from .env")

        return apiKey

    @property
    def providerModel(self) -> str:
        return self.geminiModel if self.llmProvider == "gemini" else self.openaiModel

    @model_validator(mode="after")
    def failFastOnMissingKey(self) -> "Settings":
        # Reading the property raises here, so a misconfigured .env fails at startup instead of on the first request.
        _ = self.providerApiKey
        return self

@lru_cache
def getSettings() -> Settings:
    return Settings()
