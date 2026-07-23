from fastapi import APIRouter, HTTPException

from app.agents.spotify_agent import run_agent
from app.models.agent_models import (
    AgentRequest,
    AgentResponse,
)


router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


@router.post(
    "",
    response_model=AgentResponse,
)
def execute_agent(
    request: AgentRequest,
) -> AgentResponse:
    try:
        return run_agent(
            query=request.query,
            limit=request.limit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="The Spotify agent could not process the request.",
        ) from exc

