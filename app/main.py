
from fastapi import FastAPI

from app.api.routes.search import router as search_router
from app.api.routes.agent import router as agent_router

app = FastAPI(
    title="Spotify Recommendation API",
    version="0.6.0",
)

app.include_router(search_router)
app.include_router(agent_router)

@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Spotify Recommendation API is running"
    }
