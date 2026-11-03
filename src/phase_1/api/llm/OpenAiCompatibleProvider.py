from time import perf_counter
from openai import APIConnectionError, AsyncOpenAI, OpenAIError, RateLimitError
from src.phase_1.Settings import Settings
from src.phase_1.api.llm.BaseLlmProvider import BaseLlmProvider
from src.phase_1.api.llm.LlmError import LlmError
from src.phase_1.api.llm.LlmResponse import LlmResponse

class OpenAiCompatibleProvider(BaseLlmProvider):
    """
    Every provider that speaks the OpenAI chat-completions protocol (OpenAI, Gemini, Groq, Ollama, ...)
    shares this implementation; a subclass only decides which endpoint is called.
    """
    def __init__(self, *, settings: Settings, baseUrl: str | None = None):
        self.client = AsyncOpenAI(api_key=settings.providerApiKey, base_url=baseUrl)
        self.model = settings.providerModel

    async def generate(self, *, system_prompt: str, user_message: str) -> LlmResponse:
        startedAt = perf_counter()

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
        except RateLimitError as error:
            # Rate limits and an exhausted free-tier quota both mean "come back later", not "our code broke".
            raise LlmError(str(error), statusCode=429) from error
        except APIConnectionError as error:
            raise LlmError(str(error), statusCode=503) from error
        except OpenAIError as error:
            # Every SDK failure is re-raised as our own error, so callers never import the openai package.
            raise LlmError(str(error)) from error

        latencyMs = round((perf_counter() - startedAt) * 1000)
        message = response.choices[0].message.content

        return LlmResponse(
            content=message or "",
            model=response.model,
            inputTokens=response.usage.prompt_tokens if response.usage else None,
            outputTokens=response.usage.completion_tokens if response.usage else None,
            latencyMs=latencyMs
        )

