from fastapi import APIRouter
from src.phase_1.ChatRequest import ChatRequest
from src.phase_1.ChatResponse import ChatResponse

"""
Our router wires the client and its responses to the server and responses that will be 
created by te server.
Right now it just mirrors back the request.
"""
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/ask", response_model=ChatResponse)
async def askQuestion(request: ChatRequest) -> ChatResponse:
    return ChatResponse(answer=f"You asked : {request.question}.")
