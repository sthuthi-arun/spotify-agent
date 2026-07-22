from fastapi import FastAPI
from app.api.recommendations import router as recommendations_router
from app.api.routes import router

app = FastAPI(
    title="Spotify Analytics API",
    description=(
        "A FastAPI application for searching and analysing "
        "Spotify track data stored in DuckDB."
    ),
    version="0.3.0",
)

app.include_router(
    router,
    prefix="/api/v1",
    tags=["Spotify Analytics"],
)


app.include_router(recommendations_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "Spotify Analytics API",
        "version": "0.3.0",
        "documentation": "/docs",
    }

