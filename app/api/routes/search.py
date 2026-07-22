from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.services.semantic_search import semantic_search_tracks


router = APIRouter(
    prefix="/search",
    tags=["Semantic Search"],
)


@router.get("")
def search_tracks(
    query: Annotated[
        str,
        Query(
            min_length=2,
            max_length=200,
            description="Natural-language description of music",
        ),
    ],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> dict:
    try:
        results = semantic_search_tracks(
            query=query,
            limit=limit,
        )

        return {
            "query": query,
            "result_count": len(results),
            "results": results,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

