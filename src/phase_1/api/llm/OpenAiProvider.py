from openai import AsyncOpenAI
from phase_1.Settings import Settings
from phase_1.api.llm.BaseLlmProvider import BaseLlmProvider
from phase_1.api.llm.LlmResponse import LlmResponse

class OpenAiProvider(BaseLlmProvider):
    def __init__(self, settings: Settings):
        self.client = AsyncOpenAI(api_key=settings.openaiApiKey)
        self.model = settings.openaiModel

    async def generate(self, *, system_prompt: str, user_message: str) -> LlmResponse:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

        message = response.choices[0].message.content

        return LlmResponse(
            content=message or "",
            model=response.model,
            inputTokens=response.usage.prompt_tokens if response.usage else None,
            outputTokens=response.usage.completion_tokens if response.usage else None
        )
