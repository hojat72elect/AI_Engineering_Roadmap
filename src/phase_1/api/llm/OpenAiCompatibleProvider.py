from time import perf_counter
from openai import APIConnectionError, AsyncOpenAI, InternalServerError, NotFoundError, OpenAIError, RateLimitError
from src.phase_1.Settings import Settings
from src.phase_1.api.llm.BaseLlmProvider import BaseLlmProvider
from src.phase_1.api.llm.LlmError import LlmError
from src.phase_1.api.llm.LlmResponse import LlmResponse

def providerNotFoundMessage(error: NotFoundError) -> str:
    """
    Gemini answers an unknown or retired model with a JSON *array* body, while the SDK only lifts a
    message out of a JSON *object*, so `str(error)` degrades to a bare "Error code: 404". Dig the
    provider's own sentence out of the parsed body so the log names the actual cause.
    """
    payload = error.body[0] if isinstance(error.body, list) and error.body else error.body
    details = payload.get("error") if isinstance(payload, dict) else None
    message = details.get("message") if isinstance(details, dict) else None

    return message or str(error)


class OpenAiCompatibleProvider(BaseLlmProvider):
    """
    Every provider that speaks the OpenAI chat-completions protocol (OpenAI, Gemini, Groq, Ollama, ...)
    shares this implementation; a subclass only decides which endpoint is called.
    """
    def __init__(self, *, settings: Settings, baseUrl: str | None = None):
        self.client = AsyncOpenAI(
            api_key=settings.providerApiKey,
            base_url=baseUrl,
            max_retries=settings.llmMaxRetries
        )
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
        except InternalServerError as error:
            # The provider itself is down. The SDK has already retried, so the client should back off too.
            raise LlmError(str(error), statusCode=503) from error
        except NotFoundError as error:
            # A model name the provider does not know is our own misconfiguration, not an outage.
            # 500 says so, and the provider's explanation is kept in the message for the log.
            raise LlmError(providerNotFoundMessage(error), statusCode=500) from error
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

