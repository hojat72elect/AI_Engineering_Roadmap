from abc import ABC, abstractmethod
from phase_1.api.llm.LlmResponse import LlmResponse

class BaseLlmProvider(ABC):
    """
    Any LLM that wants to be the provider to our system, needs to extend this abstract class.
    """
    @abstractmethod
    async def generate(self, *, system_prompt: str, user_message: str) -> LlmResponse:
        raise NotImplementedError
