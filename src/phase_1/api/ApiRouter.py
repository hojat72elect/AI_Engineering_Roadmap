from fastapi import APIRouter, Depends
from phase_1.api.Dependencies import getLlmProvider
from phase_1.api.llm.OpenAiProvider import OpenAiProvider
from src.phase_1.api.chat.ChatRequest import ChatRequest
from src.phase_1.api.chat.ChatResponse import ChatResponse

"""
Our router wires the client and its responses to the server and responses that will be 
created by te server.
Right now it just mirrors back the request.
"""
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/ask", response_model=ChatResponse)
async def askQuestion(request: ChatRequest, llm: OpenAiProvider = Depends(getLlmProvider)) -> ChatResponse:
    response = await llm.generate(
        system_prompt="You are a helpful AI assistant. " "Answer clearly and accurately.",
        user_message=request.question
    )

    return ChatResponse(answer=response.content)
