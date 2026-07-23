from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentIntent(str, Enum):
    SEARCH_TRACKS = "search_tracks"
    RECOMMEND_TRACKS = "recommend_tracks"
    ARTIST_ANALYTICS = "artist_analytics"
    TRACK_ANALYTICS = "track_analytics"
    GENERAL_QUESTION = "general_question"
    UNSUPPORTED = "unsupported"


class AgentRequest(BaseModel):
    query: str = Field(
        min_length=2,
        max_length=500,
        description="Natural-language Spotify dataset request",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class AgentPlan(BaseModel):
    intent: AgentIntent
    search_query: str
    explanation: str


class AgentResponse(BaseModel):
    query: str
    intent: AgentIntent
    explanation: str
    result_count: int
    results: list[dict[str, Any]]
