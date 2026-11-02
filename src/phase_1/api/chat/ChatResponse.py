from pydantic import BaseModel


class ChatMetadata(BaseModel):
    """
    Everything the client may want to know about how the answer was produced.
    """
    model: str | None = None
    latencyMs: int | None = None
    inputTokens: int | None = None
    outputTokens: int | None = None


class ChatResponse(BaseModel):
    """
    Any of the responses that server sends back to the client.
    """
    answer: str
    metadata: ChatMetadata

