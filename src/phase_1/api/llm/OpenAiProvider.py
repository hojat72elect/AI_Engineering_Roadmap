from src.phase_1.Settings import Settings
from src.phase_1.api.llm.OpenAiCompatibleProvider import OpenAiCompatibleProvider

class OpenAiProvider(OpenAiCompatibleProvider):
    """
    OpenAI's own endpoint. The base class already defaults to it, so there is nothing to override.
    """
    def __init__(self, settings: Settings):
        super().__init__(settings=settings)

