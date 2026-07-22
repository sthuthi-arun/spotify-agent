from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

from app.database.connection import get_connection


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def semantic_search_tracks(
    query: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    if not query.strip():
        raise ValueError("Search query cannot be empty")

    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    model = get_embedding_model()

    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                e.track_id,
                e.embedding,
                t.track_name,
                t.artists,
                t.album_name,
                t.track_genre,
                t.popularity
            FROM track_embeddings AS e
            INNER JOIN raw_tracks AS t
                ON e.track_id = t.track_id
            """
        ).fetchall()

    results: list[dict[str, Any]] = []

    for row in rows:
        stored_embedding = np.asarray(row[1], dtype=np.float32)

        norm = np.linalg.norm(stored_embedding)

        if norm == 0:
            continue

        stored_embedding = stored_embedding / norm

        similarity = float(
            np.dot(query_embedding, stored_embedding)
        )

        results.append(
            {
                "track_id": row[0],
                "track_name": row[2],
                "artists": row[3],
                "album_name": row[4],
                "genre": row[5],
                "popularity": row[6],
                "similarity_score": round(similarity, 4),
            }
        )

    results.sort(
        key=lambda item: item["similarity_score"],
        reverse=True,
    )

    return results[:limit]

