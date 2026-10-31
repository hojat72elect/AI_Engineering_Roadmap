from fastapi import FastAPI
from src.phase_1.ApiRouter import router as chatRouter

def createApp() -> FastAPI:
    fastApiApp = FastAPI(title="App phase 1", version="0.0.1")

    @fastApiApp.get("/health")
    async def healthCheck():
        """
        Simply checks if the API itself is up and running.
        """
        return {"status": "ok"}

    fastApiApp.include_router(chatRouter, prefix="/api/v1")

    return fastApiApp

app = createApp()
