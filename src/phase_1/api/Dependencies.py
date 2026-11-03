"""
Inside the `api` directory, if there's need for dependency injection, the function that performs the DI is defined in this file.
"""
from functools import lru_cache
from fastapi import Depends
from src.phase_1.Settings import getSettings
from src.phase_1.api.chat.ChatService import ChatService
from src.phase_1.api.llm.BaseLlmProvider import BaseLlmProvider
from src.phase_1.api.llm.GeminiProvider import GeminiProvider
from src.phase_1.api.llm.OpenAiProvider import OpenAiProvider

@lru_cache
def getLlmProvider() -> BaseLlmProvider:
    settings = getSettings()

    if settings.llmProvider == "gemini":
        return GeminiProvider(settings=settings)

    return OpenAiProvider(settings=settings)

def getChatService(llm=Depends(getLlmProvider)) -> ChatService:
    return ChatService(llm=llm)
