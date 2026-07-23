from typing import Any, Sequence

from app.database.connection import get_connection


def execute_query(
    sql: str,
    parameters: Sequence[Any] | None = None,
) -> list[dict[str, Any]]:
    with get_connection() as connection:
        result = connection.execute(
            sql,
            parameters or [],
        )

        column_names = [
            column[0]
            for column in result.description
        ]

        rows = result.fetchall()

    return [
        dict(zip(column_names, row))
        for row in rows
    ]

def rows_to_dicts(
    column_names: list[str],
    rows: list[tuple],
) -> list[dict[str, Any]]:
    return [
        dict(zip(column_names, row))
        for row in rows
    ]
    
    
def rank_artists_by_album_count(
    limit: int = 20,
) -> list[dict[str, Any]]:
    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100")

    sql = """
        SELECT
            artists,
            COUNT(DISTINCT album_name) AS album_count,
            COUNT(DISTINCT track_id) AS track_count,
            DENSE_RANK() OVER (
                ORDER BY COUNT(DISTINCT album_name) DESC
            ) AS artist_rank
        FROM raw_tracks
        WHERE artists IS NOT NULL
          AND album_name IS NOT NULL
        GROUP BY artists
        ORDER BY artist_rank, artists
        LIMIT ?
    """

    return execute_query(sql, [limit])
    
def search_tracks(
    query: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty")

    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100")

    sql = """
        SELECT
            track_id,
            track_name,
            artists,
            album_name,
            track_genre,
            popularity
        FROM raw_tracks
        WHERE track_name ILIKE ?
           OR artists ILIKE ?
        ORDER BY popularity DESC, track_name
        LIMIT ?
    """

    search_pattern = f"%{query}%"

    return execute_query(
        sql,
        [search_pattern, search_pattern, limit],
    )
    

def get_top_tracks_by_genre(
    genre: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    genre = genre.strip()

    if not genre:
        raise ValueError("Genre cannot be empty")

    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100")

    sql = """
        SELECT
            track_id,
            track_name,
            artists,
            album_name,
            track_genre,
            popularity,
            energy,
            danceability
        FROM raw_tracks
        WHERE LOWER(track_genre) = LOWER(?)
        ORDER BY popularity DESC, track_name
        LIMIT ?
    """

    return execute_query(sql, [genre, limit])

def find_track_by_name(
    track_name: str,
) -> dict[str, Any] | None:
    cleaned_name = track_name.strip()

    if not cleaned_name:
        raise ValueError("Track name cannot be empty")

    sql = """
        SELECT
            track_id,
            track_name,
            artists,
            album_name,
            track_genre,
            popularity,
            duration_ms,
            explicit
        FROM raw_tracks
        WHERE LOWER(track_name) = LOWER(?)
        ORDER BY popularity DESC NULLS LAST
        LIMIT 1
    """

    exact_results = execute_query(sql, [cleaned_name])

    if exact_results:
        return exact_results[0]

    partial_sql = """
        SELECT
            track_id,
            track_name,
            artists,
            album_name,
            track_genre,
            popularity,
            duration_ms,
            explicit
        FROM raw_tracks
        WHERE LOWER(track_name) LIKE LOWER(?)
        ORDER BY
            CASE
                WHEN LOWER(track_name) LIKE LOWER(?) THEN 0
                ELSE 1
            END,
            popularity DESC NULLS LAST
        LIMIT 1
    """

    partial_results = execute_query(
        partial_sql,
        [
            f"%{cleaned_name}%",
            f"{cleaned_name}%",
        ],
    )

    if not partial_results:
        return None

    return partial_results[0]

def get_track_by_id(track_id: str) -> dict[str, Any] | None:
    sql = """
        SELECT
            track_id,
            track_name,
            artists,
            album_name,
            track_genre,
            popularity,
            duration_ms,
            explicit
        FROM raw_tracks
        WHERE track_id = ?
        LIMIT 1
    """

    results = execute_query(sql, [track_id])

    if not results:
        return None

    return results[0]


def recommend_similar_tracks(
    track_id: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    sql = """
        WITH selected_track AS (
            SELECT
                track_id,
                track_genre,
                popularity,
                duration_ms,
                explicit
            FROM raw_tracks
            WHERE track_id = ?
            LIMIT 1
        )
        SELECT
            candidate.track_id,
            candidate.track_name,
            candidate.artists,
            candidate.album_name,
            candidate.track_genre,
            candidate.popularity,
            candidate.duration_ms,
            candidate.explicit,

            ABS(
                candidate.popularity - selected.popularity
            ) AS popularity_difference,

            ABS(
                candidate.duration_ms - selected.duration_ms
            ) AS duration_difference,

            (
                ABS(candidate.popularity - selected.popularity)
                +
                ABS(candidate.duration_ms - selected.duration_ms) / 10000.0
            ) AS similarity_score

        FROM raw_tracks AS candidate
        CROSS JOIN selected_track AS selected

        WHERE candidate.track_id <> selected.track_id
          AND candidate.track_genre = selected.track_genre
          AND candidate.explicit = selected.explicit
          AND candidate.popularity IS NOT NULL
          AND candidate.duration_ms IS NOT NULL

        ORDER BY
            similarity_score ASC,
            candidate.popularity DESC,
            candidate.track_name

        LIMIT ?
    """

    return execute_query(sql, [track_id, limit])
