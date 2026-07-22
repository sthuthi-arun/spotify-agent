from typing import Any

from app.database.connection import get_connection
from app.database.documents import build_track_document


def create_embedding_tables() -> None:
    """
    Create tables for track documents and embeddings.
    """

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS track_documents (
                track_id VARCHAR PRIMARY KEY,
                document_text VARCHAR NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS track_embeddings (
                track_id VARCHAR NOT NULL,
                model_name VARCHAR NOT NULL,
                dimension INTEGER NOT NULL,
                embedding DOUBLE[] NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (track_id, model_name)
            )
            """
        )


def generate_track_documents() -> int:
    """
    Read tracks from raw_tracks and create one text document per track.
    """

    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT
                track_id,
                track_name,
                artists,
                album_name,
                track_genre,
                popularity,
                danceability,
                energy,
                acousticness,
                instrumentalness,
                valence,
                tempo
            FROM raw_tracks
            WHERE track_id IS NOT NULL
            """
        )

        rows = cursor.fetchall()

        column_names = [
            description[0]
            for description in cursor.description
        ]

        document_records: list[tuple[str, str]] = []

        for row in rows:
            track = dict(zip(column_names, row))

            document_text = build_track_document(track)

            document_records.append(
                (
                    str(track["track_id"]),
                    document_text,
                )
            )

        if document_records:
            connection.executemany(
                """
                INSERT OR REPLACE INTO track_documents (
                    track_id,
                    document_text,
                    updated_at
                )
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                document_records,
            )

    return len(document_records)


def get_documents_without_embeddings(
    model_name: str,
    limit: int = 500,
) -> list[dict[str, Any]]:
    """
    Return documents that do not yet have an embedding for this model.
    """

    if limit < 1:
        raise ValueError("Limit must be greater than zero")

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                documents.track_id,
                documents.document_text
            FROM track_documents AS documents
            LEFT JOIN track_embeddings AS embeddings
                ON documents.track_id = embeddings.track_id
               AND embeddings.model_name = ?
            WHERE embeddings.track_id IS NULL
            LIMIT ?
            """,
            [model_name, limit],
        ).fetchall()

    return [
        {
            "track_id": row[0],
            "document_text": row[1],
        }
        for row in rows
    ]


def save_embeddings(
    model_name: str,
    embeddings: list[tuple[str, list[float]]],
) -> None:
    """
    Save generated embedding vectors in DuckDB.
    """

    if not embeddings:
        return

    records = [
        (
            track_id,
            model_name,
            len(vector),
            vector,
        )
        for track_id, vector in embeddings
    ]

    with get_connection() as connection:
        connection.executemany(
            """
            INSERT OR REPLACE INTO track_embeddings (
                track_id,
                model_name,
                dimension,
                embedding,
                created_at
            )
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            records,
        )


def count_documents() -> int:
    with get_connection() as connection:
        result = connection.execute(
            """
            SELECT COUNT(*)
            FROM track_documents
            """
        ).fetchone()

    return int(result[0])


def count_embeddings() -> int:
    with get_connection() as connection:
        result = connection.execute(
            """
            SELECT COUNT(*)
            FROM track_embeddings
            """
        ).fetchone()

    return int(result[0])

