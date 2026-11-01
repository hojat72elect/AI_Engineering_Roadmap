"""
Inside the `api` directory, if there's need for dependency injection, the function that performs the DI is defined in this file.
"""
from functools import lru_cache
from phase_1.api.llm.OpenAiProvider import OpenAiProvider
from phase_1.Settings import getSettings

@lru_cache
def getLlmProvider() -> OpenAiProvider:
    settings = getSettings()
    return OpenAiProvider(settings=settings)
