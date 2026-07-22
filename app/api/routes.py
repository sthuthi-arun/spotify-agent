from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.database.repository import (
    get_top_tracks_by_genre,
    rank_artists_by_album_count,
    search_tracks,
)

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/tracks/search")
def search_for_tracks(
    query: Annotated[
        str,
        Query(
            min_length=1,
            max_length=100,
            description="Track, artist, or album name",
        ),
    ],
    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
) -> dict:
    try:
        tracks = search_tracks(query=query, limit=limit)

        return {
            "query": query,
            "count": len(tracks),
            "results": tracks,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/genres/{genre}/top-tracks")
def top_tracks_by_genre(
    genre: str,
    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
) -> dict:
    try:
        tracks = get_top_tracks_by_genre(
            genre=genre,
            limit=limit,
        )

        if not tracks:
            raise HTTPException(
                status_code=404,
                detail=f"No tracks found for genre '{genre}'",
            )

        return {
            "genre": genre,
            "count": len(tracks),
            "results": tracks,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/artists/rankings")
def artist_rankings(
    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
) -> dict:
    try:
        artists = rank_artists_by_album_count(limit=limit)

        return {
            "count": len(artists),
            "results": artists,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

