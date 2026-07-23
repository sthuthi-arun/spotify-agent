import re

from app.models.agent import AgentIntent, AgentPlan


def classify_agent_request(message: str) -> AgentPlan:
    normalized_message = message.strip().lower()

    limit = _extract_limit(normalized_message)

    if _contains_any(
        normalized_message,
        [
            "recommend",
            "recommendation",
            "similar to",
            "songs like",
            "tracks like",
        ],
    ):
        return AgentPlan(
            intent=AgentIntent.RECOMMEND_TRACKS,
            search_query=message.strip(),
            limit=limit,
            explanation=(
                "The request asks for recommendations or tracks similar "
                "to another track."
            ),
        )

    if _contains_any(
        normalized_message,
        [
            "find",
            "search",
            "show me",
            "give me songs",
            "give me tracks",
            "music for",
            "songs for",
            "tracks for",
        ],
    ):
        return AgentPlan(
            intent=AgentIntent.SEARCH_TRACKS,
            search_query=_clean_search_query(message),
            limit=limit,
            explanation=(
                "The request asks the agent to find tracks matching "
                "a description."
            ),
        )

    if _contains_any(
        normalized_message,
        [
            "top artist",
            "most albums",
            "most tracks",
            "artist statistics",
            "artist analytics",
            "rank artists",
        ],
    ):
        return AgentPlan(
            intent=AgentIntent.ARTIST_ANALYTICS,
            limit=limit,
            explanation=(
                "The request asks for statistics or rankings about artists."
            ),
        )

    if _contains_any(
        normalized_message,
        [
            "most popular track",
            "track statistics",
            "track analytics",
            "highest energy",
            "most danceable",
            "least popular",
        ],
    ):
        return AgentPlan(
            intent=AgentIntent.TRACK_ANALYTICS,
            limit=limit,
            explanation=(
                "The request asks for statistics or rankings about tracks."
            ),
        )

    if _contains_any(
        normalized_message,
        [
            "what can you do",
            "help",
            "who are you",
            "how does this work",
        ],
    ):
        return AgentPlan(
            intent=AgentIntent.GENERAL_QUESTION,
            limit=limit,
            explanation=(
                "The request is about the capabilities or behaviour "
                "of the agent."
            ),
        )

    return AgentPlan(
        intent=AgentIntent.UNSUPPORTED,
        limit=limit,
        explanation=(
            "The request could not be confidently mapped to a supported tool."
        ),
    )


def _contains_any(message: str, phrases: list[str]) -> bool:
    return any(phrase in message for phrase in phrases)


def _extract_limit(message: str, default: int = 5) -> int:
    match = re.search(
        r"\b(?:top|find|show|give|recommend)?\s*(\d{1,3})\b",
        message,
    )

    if match is None:
        return default

    requested_limit = int(match.group(1))
    return max(1, min(requested_limit, 20))


def _clean_search_query(message: str) -> str:
    cleaned_message = message.strip()

    prefixes = [
        r"^find\s+",
        r"^search\s+for\s+",
        r"^search\s+",
        r"^show\s+me\s+",
        r"^give\s+me\s+",
    ]

    for prefix in prefixes:
        cleaned_message = re.sub(
            prefix,
            "",
            cleaned_message,
            flags=re.IGNORECASE,
        )

    cleaned_message = re.sub(
        r"\b(?:top\s+)?\d{1,3}\b",
        "",
        cleaned_message,
        flags=re.IGNORECASE,
    )

    cleaned_message = re.sub(r"\s+", " ", cleaned_message)

    return cleaned_message.strip(" .?!")
