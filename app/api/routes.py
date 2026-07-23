from fastapi import APIRouter

from app.models.agent import AgentRequest, AgentResponse
from app.services.agent_service import handle_agent_request


router = APIRouter()


@router.post(
    "/agent",
    response_model=AgentResponse,
    summary="Process a natural-language Spotify request",
)
def agent(request: AgentRequest) -> AgentResponse:
    return handle_agent_request(request)
