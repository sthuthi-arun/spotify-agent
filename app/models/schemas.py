from pydantic import BaseModel


class TrackResponse(BaseModel):
    track_id: str
    track_name: str | None = None
    artists: str | None = None
    album_name: str | None = None
    track_genre: str | None = None
    popularity: int | None = None
    duration_ms: int | None = None
    explicit: bool | None = None


class RecommendedTrackResponse(TrackResponse):
    popularity_difference: int
    duration_difference: int
    similarity_score: float


class RecommendationResponse(BaseModel):
    selected_track: TrackResponse
    recommendations: list[RecommendedTrackResponse]
