import logging
import re
from typing import Any


logger = logging.getLogger(__name__)

from app.database.repository import (
    find_track_by_name,
    rank_artists_by_album_count,
    recommend_similar_tracks,
)
from app.models.agent_models import (
    AgentIntent,
    AgentPlan,
    AgentResponse,
)
from app.services.semantic_search import semantic_search_tracks


RECOMMENDATION_PATTERNS = (
    "recommend",
    "recommendation",
    "similar to",
    "songs like",
    "tracks like",
    "music like",
)

ARTIST_ANALYTICS_PATTERNS = (
    "top artists",
    "most albums",
    "artist ranking",
    "rank artists",
    "artists with",
)

TRACK_ANALYTICS_PATTERNS = (
    "top tracks",
    "popular tracks",
    "most popular",
    "highest popularity",
)

SEARCH_PATTERNS = (
    "find",
    "search",
    "show",
    "give me",
    "looking for",
)


def clean_query(query: str) -> str:
    return " ".join(query.strip().split())


def extract_recommendation_track_name(query: str) -> str:
    patterns = (
        r"similar to\s+(.+)",
        r"songs like\s+(.+)",
        r"tracks like\s+(.+)",
        r"music like\s+(.+)",
        r"recommend.*(?:based on|for)\s+(.+)",
        r"recommend\s+(.+)",
    )

    for pattern in patterns:
        match = re.search(
            pattern,
            query,
            flags=re.IGNORECASE,
        )

        if match:
            track_name = match.group(1).strip()
            return track_name.strip("\"'.")

    return query


def classify_intent(query: str) -> AgentPlan:
    cleaned_query = clean_query(query)
    lowered_query = cleaned_query.lower()

    if any(
        pattern in lowered_query
        for pattern in RECOMMENDATION_PATTERNS
    ):
        track_name = extract_recommendation_track_name(cleaned_query)

        return AgentPlan(
            intent=AgentIntent.RECOMMEND_TRACKS,
            search_query=track_name,
            explanation=(
                "The request asks for tracks similar to another track."
            ),
        )

    if any(
        pattern in lowered_query
        for pattern in ARTIST_ANALYTICS_PATTERNS
    ):
        return AgentPlan(
            intent=AgentIntent.ARTIST_ANALYTICS,
            search_query=cleaned_query,
            explanation=(
                "The request asks for an artist-level dataset ranking."
            ),
        )

    if any(
        pattern in lowered_query
        for pattern in TRACK_ANALYTICS_PATTERNS
    ):
        return AgentPlan(
            intent=AgentIntent.TRACK_ANALYTICS,
            search_query=cleaned_query,
            explanation=(
                "The request asks for popular or highly ranked tracks."
            ),
        )

    if any(
        pattern in lowered_query
        for pattern in SEARCH_PATTERNS
    ):
        return AgentPlan(
            intent=AgentIntent.SEARCH_TRACKS,
            search_query=cleaned_query,
            explanation=(
                "The request asks to find tracks matching a description."
            ),
        )

    return AgentPlan(
        intent=AgentIntent.SEARCH_TRACKS,
        search_query=cleaned_query,
        explanation=(
            "The request will be handled using semantic track search."
        ),
    )


def run_track_search(
    query: str,
    limit: int,
) -> list[dict[str, Any]]:
    return semantic_search_tracks(
        query=query,
        limit=limit,
    )


def run_recommendation(
    track_name: str,
    limit: int,
) -> list[dict[str, Any]]:
    selected_track = find_track_by_name(track_name)

    if selected_track is None:
        semantic_matches = semantic_search_tracks(
            query=track_name,
            limit=1,
        )

        if not semantic_matches:
            return []

        selected_track = semantic_matches[0]

    track_id = selected_track.get("track_id")

    if not track_id:
        return []

    recommendations = recommend_similar_tracks(
        track_id=track_id,
        limit=limit,
    )

    for recommendation in recommendations:
        recommendation["based_on_track"] = {
            "track_id": selected_track.get("track_id"),
            "track_name": selected_track.get("track_name"),
            "artists": selected_track.get("artists"),
        }

    return recommendations


def run_artist_analytics(
    limit: int,
) -> list[dict[str, Any]]:
    return rank_artists_by_album_count(limit=limit)

def remove_duplicate_tracks(
    results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    unique_results: list[dict[str, Any]] = []
    seen_track_ids: set[str] = set()
    seen_track_details: set[tuple[str, str]] = set()

    for result in results:
        track_id = str(result.get("track_id") or "").strip()
        track_name = str(result.get("track_name") or "").strip().lower()
        artists = str(result.get("artists") or "").strip().lower()

        if track_id:
            if track_id in seen_track_ids:
                continue

            seen_track_ids.add(track_id)

        elif track_name:
            fallback_key = (track_name, artists)

            if fallback_key in seen_track_details:
                continue

            seen_track_details.add(fallback_key)

        unique_results.append(result)

    return unique_results


def run_agent(
    query: str,
    limit: int = 5,
) -> AgentResponse:
    cleaned_query = clean_query(query)

    if len(cleaned_query) < 2:
        raise ValueError(
            "Query must contain at least 2 characters"
        )

    if len(cleaned_query) > 500:
        raise ValueError(
            "Query cannot exceed 500 characters"
        )

    if not 1 <= limit <= 20:
        raise ValueError(
            "Limit must be between 1 and 20"
        )

    logger.info(
        "Processing agent request query=%r limit=%s",
        cleaned_query,
        limit,
    )

    plan = classify_intent(cleaned_query)

    logger.info(
        "Detected intent=%s search_query=%r",
        plan.intent.value,
        plan.search_query,
    )

    if plan.intent == AgentIntent.RECOMMEND_TRACKS:
        results = run_recommendation(
            track_name=plan.search_query,
            limit=limit,
        )

    elif plan.intent == AgentIntent.ARTIST_ANALYTICS:
        results = run_artist_analytics(limit=limit)

    elif plan.intent in (
        AgentIntent.SEARCH_TRACKS,
        AgentIntent.TRACK_ANALYTICS,
    ):
        results = run_track_search(
            query=plan.search_query,
            limit=limit,
        )

    else:
        results = []

    cleaned_results = remove_duplicate_tracks(results)
    cleaned_results = cleaned_results[:limit]

    if not cleaned_results:
        explanation = (
            f"{plan.explanation} "
            "No matching results were found."
        )
    else:
        explanation = plan.explanation

    logger.info(
        "Agent request completed intent=%s result_count=%s",
        plan.intent.value,
        len(cleaned_results),
    )

    return AgentResponse(
        query=cleaned_query,
        intent=plan.intent,
        explanation=explanation,
        result_count=len(cleaned_results),
        results=cleaned_results,
    )
