from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """
    Any of the requests that client sends to server.
    """
    question: str = Field(min_length=1, max_length=10_000, description="The user's question from AI")
