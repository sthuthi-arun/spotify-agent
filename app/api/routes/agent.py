from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agents.spotify_agent import spotify_agent


router = APIRouter(
    prefix="/agent",
    tags=["Spotify Agent"],
)


class AgentRequest(BaseModel):
    query: str = Field(
        min_length=2,
        max_length=300,
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
    )


@router.post("")
def run_agent(request: AgentRequest) -> dict:
    result = spotify_agent.invoke(
        {
            "query": request.query,
            "limit": request.limit,
        }
    )

    results = result.get("results", [])

    return {
        "query": request.query,
        "intent": result.get("intent"),
        "message": result.get("message"),
        "result_count": len(results),
        "results": results,
    }
