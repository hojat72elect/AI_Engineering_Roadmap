from pydantic import BaseModel

class LlmResponse(BaseModel):
    content: str
    inputTokens: int | None = None
    outputTokens: int | None = None
    model: str | None = None
    latencyMs: int | None = None
