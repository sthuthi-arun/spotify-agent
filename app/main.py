
from fastapi import FastAPI

from app.api.routes.search import router as search_router
from app.api.agent import router as agent_router
from app.core.logging_config import configure_logging


from app.core.config import settings


configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A Spotify dataset API supporting analytical SQL, "
        "semantic search, recommendations, and "
        "natural-language request routing."
    ),
)

app.include_router(search_router)
app.include_router(agent_router)

@app.get(
    "/",
    tags=["health"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
    

