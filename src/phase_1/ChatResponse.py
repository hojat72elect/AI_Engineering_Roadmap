from pydantic import BaseModel


class ChatResponse(BaseModel):
    """
    Any of the responses that server sends back to the client.
    """
    answer: str

