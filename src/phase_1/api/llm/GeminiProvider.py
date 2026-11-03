from src.phase_1.Settings import Settings
from src.phase_1.api.llm.OpenAiCompatibleProvider import OpenAiCompatibleProvider

class GeminiProvider(OpenAiCompatibleProvider):
    """
    Gemini exposes an OpenAI-compatible endpoint, so the base URL is the only vendor-specific detail.
    """
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

    def __init__(self, settings: Settings):
        super().__init__(settings=settings, baseUrl=self.BASE_URL)

