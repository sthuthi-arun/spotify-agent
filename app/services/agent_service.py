from typing import Any

from app.models.agent import (
    AgentIntent,
    AgentRequest,
    AgentResponse,
)
from app.services.agent_router import classify_agent_request

# Change these imports only if your existing function names differ.
from app.services.embedding_service import semantic_search
from app.repositories.track_repository import (
    rank_artists_by_album_count,
)


def handle_agent_request(request: AgentRequest) -> AgentResponse:
    plan = classify_agent_request(request.message)

    try:
        results = execute_plan(plan)

        return AgentResponse(
            message=create_response_message(
                intent=plan.intent,
                result_count=len(results),
            ),
            intent=plan.intent,
            results=results,
            plan=plan,
            conversation_id=request.conversation_id,
            success=True,
        )

    except ValueError as error:
        return AgentResponse(
            message="I could not process that request.",
            intent=plan.intent,
            results=[],
            plan=plan,
            conversation_id=request.conversation_id,
            success=False,
            error=str(error),
        )

    except Exception as error:
        return AgentResponse(
            message="An unexpected error occurred while processing the request.",
            intent=plan.intent,
            results=[],
            plan=plan,
            conversation_id=request.conversation_id,
            success=False,
            error=str(error),
        )


def execute_plan(plan: Any) -> list[dict[str, Any]]:
    if plan.intent == AgentIntent.SEARCH_TRACKS:
        if not plan.search_query:
            raise ValueError("A search description is required.")

        return semantic_search(
            query=plan.search_query,
            limit=plan.limit,
        )

    if plan.intent == AgentIntent.ARTIST_ANALYTICS:
        return rank_artists_by_album_count(
            limit=plan.limit,
        )

    if plan.intent == AgentIntent.GENERAL_QUESTION:
        return [
            {
                "capability": "semantic_search",
                "description": (
                    "Find tracks using natural-language descriptions."
                ),
            },
            {
                "capability": "artist_analytics",
                "description": (
                    "Rank artists using album and track statistics."
                ),
            },
            {
                "capability": "recommendations",
                "description": (
                    "Recommend tracks similar to a selected track."
                ),
            },
        ]

    if plan.intent == AgentIntent.RECOMMEND_TRACKS:
        raise ValueError(
            "Recommendation requests require a track to be resolved first."
        )

    if plan.intent == AgentIntent.TRACK_ANALYTICS:
        raise ValueError(
            "Track analytics routing has not been connected yet."
        )

    raise ValueError(
        "This request is outside the Spotify agent's supported capabilities."
    )


def create_response_message(
    intent: AgentIntent,
    result_count: int,
) -> str:
    if intent == AgentIntent.SEARCH_TRACKS:
        return f"I found {result_count} matching tracks."

    if intent == AgentIntent.ARTIST_ANALYTICS:
        return f"I found {result_count} ranked artists."

    if intent == AgentIntent.GENERAL_QUESTION:
        return "Here are the operations I currently support."

    return f"The request returned {result_count} results."
