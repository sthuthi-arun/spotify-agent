from fastapi import APIRouter

from app.agents.spotify_agent import spotify_agent
from app.models.agent import AgentIntent, AgentRequest, AgentResponse


router = APIRouter(
    prefix="/agent",
    tags=["Spotify Agent"],
)


INTENT_MAPPING: dict[str, AgentIntent] = {
    "semantic_search": AgentIntent.SEARCH_TRACKS,
    "search": AgentIntent.SEARCH_TRACKS,
    "search_tracks": AgentIntent.SEARCH_TRACKS,

    "recommendation": AgentIntent.RECOMMEND_TRACKS,
    "recommendations": AgentIntent.RECOMMEND_TRACKS,
    "recommend_tracks": AgentIntent.RECOMMEND_TRACKS,

    "artist_analytics": AgentIntent.ARTIST_ANALYTICS,
    "track_analytics": AgentIntent.TRACK_ANALYTICS,

    "general_question": AgentIntent.GENERAL_QUESTION,
    "unsupported": AgentIntent.UNSUPPORTED,
}


def normalize_intent(raw_intent: str | None) -> AgentIntent:
    if raw_intent is None:
        return AgentIntent.UNSUPPORTED

    return INTENT_MAPPING.get(
        raw_intent.strip().lower(),
        AgentIntent.UNSUPPORTED,
    )


@router.post(
    "",
    response_model=AgentResponse,
    summary="Process a natural-language Spotify request",
)
def run_agent(request: AgentRequest) -> AgentResponse:
    try:
        result = spotify_agent.invoke(
            {
                "query": request.message,
                "limit": request.limit,
                "conversation_id": request.conversation_id,
            }
        )

        results = result.get("results", [])
        intent = normalize_intent(result.get("intent"))

        return AgentResponse(
            message=result.get(
                "message",
                f"The request returned {len(results)} results.",
            ),
            intent=intent,
            results=results,
            plan=None,
            conversation_id=request.conversation_id,
            success=True,
            error=None,
        )

    except ValueError as error:
        return AgentResponse(
            message="I could not process that request.",
            intent=AgentIntent.UNSUPPORTED,
            results=[],
            plan=None,
            conversation_id=request.conversation_id,
            success=False,
            error=str(error),
        )

    except Exception as error:
        return AgentResponse(
            message="An unexpected error occurred while processing the request.",
            intent=AgentIntent.UNSUPPORTED,
            results=[],
            plan=None,
            conversation_id=request.conversation_id,
            success=False,
            error=str(error),
        )
