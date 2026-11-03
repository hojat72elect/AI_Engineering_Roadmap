import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.phase_1.api.ApiRouter import router as chatRouter
from src.phase_1.api.llm.LlmError import LlmError

logger = logging.getLogger(__name__)

# Clients get one of these instead of the provider's raw error, so internals never leak while
# "temporarily unavailable" stays distinguishable from "you hit a quota".
PROVIDER_ERROR_MESSAGES = {
    429: "The AI provider reached its rate or quota limit. Please try again later.",
    503: "The AI provider is temporarily unavailable. Please try again in a moment."
}
DEFAULT_PROVIDER_ERROR_MESSAGE = "The AI provider could not answer. Please try again later."

def createApp() -> FastAPI:
    fastApiApp = FastAPI(title="App phase 1", version="0.0.1")

    @fastApiApp.exception_handler(LlmError)
    async def llmErrorHandler(request: Request, error: LlmError) -> JSONResponse:
        """
        Turns any provider failure into a single, stable error contract for the client.
        The provider's own message is logged rather than returned, so we never leak internals.
        """
        logger.exception("The LLM provider failed to answer %s", request.url.path)
        return JSONResponse(
            status_code=error.statusCode,
            content={"detail": PROVIDER_ERROR_MESSAGES.get(error.statusCode, DEFAULT_PROVIDER_ERROR_MESSAGE)}
        )

    @fastApiApp.get("/health")
    async def healthCheck():
        """
        Simply checks if the API itself is up and running.
        """
        return {"status": "ok"}

    fastApiApp.include_router(chatRouter, prefix="/api/v1")

    return fastApiApp

app = createApp()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.phase_1.MainApp:app", host="127.0.0.1", port=8000, reload=True)
