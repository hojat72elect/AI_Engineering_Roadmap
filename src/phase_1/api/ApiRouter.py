from fastapi import APIRouter, Depends
from src.phase_1.api.Dependencies import getChatService
from src.phase_1.api.chat.ChatService import ChatService
from src.phase_1.api.chat.ChatRequest import ChatRequest
from src.phase_1.api.chat.ChatResponse import ChatResponse

"""
Our router wires the client and its responses to the server and responses that will be 
created by te server.
The router only knows about the chat service, never about the provider that produced the answer.
"""
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=ChatResponse)
async def askQuestion(request: ChatRequest, chatService: ChatService = Depends(getChatService)) -> ChatResponse:
    return await chatService.ask(question=request.question)
