from src.phase_1.api.chat.ChatResponse import ChatMetadata, ChatResponse
from src.phase_1.api.llm.BaseLlmProvider import BaseLlmProvider

class ChatService:
    """
    This service sits between the API router and the LLM providers.
    """
    def __init__(self, llm: BaseLlmProvider):
        self.llm = llm

    async def ask(self, question: str) -> ChatResponse:
        response = await self.llm.generate(
            system_prompt="You are a helpful AI assistant. " "Provide concise and accurate answers.",
            user_message=question
        )

        return ChatResponse(
            answer=response.content,
            metadata=ChatMetadata(
                model=response.model,
                latencyMs=response.latencyMs,
                inputTokens=response.inputTokens,
                outputTokens=response.outputTokens
            )
        )

