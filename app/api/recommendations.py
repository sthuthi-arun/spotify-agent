from fastapi import APIRouter, HTTPException, Query, status

from app.database.repository import (
    get_track_by_id,
    recommend_similar_tracks,
)
from app.models.schemas import RecommendationResponse


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.get(
    "/tracks/{track_id}",
    response_model=RecommendationResponse,
)
def get_track_recommendations(
    track_id: str,
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of recommendations",
    ),
) -> RecommendationResponse:
    selected_track = get_track_by_id(track_id)

    if selected_track is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track '{track_id}' was not found",
        )

    recommendations = recommend_similar_tracks(
        track_id=track_id,
        limit=limit,
    )

    return RecommendationResponse(
        selected_track=selected_track,
        recommendations=recommendations,
    )

