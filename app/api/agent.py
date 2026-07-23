from fastapi import APIRouter, HTTPException
import logging
from app.agents.spotify_agent import run_agent
from app.models.agent_models import (
    AgentRequest,
    AgentResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


@router.post(
    "",
    response_model=AgentResponse,
    summary="Process a natural-language Spotify request",
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
        logger.warning(
            "Invalid agent request: %s",
            exc,
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception(
            "Unexpected error while processing agent request"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "The Spotify agent could not process the request."
            ),
        )
