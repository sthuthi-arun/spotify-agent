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
    message: str = Field(
        min_length=2,
        max_length=1000,
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    conversation_id: str | None = None


class AgentPlan(BaseModel):
    intent: AgentIntent
    search_query: str | None = None
    track_id: str | None = None
    artist_name: str | None = None
    limit: int = Field(default=5, ge=1, le=20)
    explanation: str


class AgentResponse(BaseModel):
    message: str
    intent: AgentIntent
    results: list[dict[str, Any]] = Field(default_factory=list)
    plan: AgentPlan | None = None
    conversation_id: str | None = None
    success: bool = True
    error: str | None = None
