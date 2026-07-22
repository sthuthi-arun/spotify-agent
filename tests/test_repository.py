import pytest

from app.database.repository import (
    get_top_tracks_by_genre,
    rank_artists_by_album_count,
    search_tracks,
)


def test_get_top_tracks_by_genre() -> None:
    results = get_top_tracks_by_genre("pop", 5)

    assert len(results) <= 5
    assert len(results) > 0
    assert all(
        row["track_genre"].lower() == "pop"
        for row in results
    )


def test_search_tracks() -> None:
    results = search_tracks("weeknd", 5)

    assert len(results) <= 5
    assert len(results) > 0

    for row in results:
        combined_text = (
            f"{row['track_name']} {row['artists']}"
        ).lower()

        assert "weeknd" in combined_text


def test_rank_artists_by_album_count() -> None:
    results = rank_artists_by_album_count(10)

    assert len(results) <= 10
    assert len(results) > 0

    album_counts = [
        row["album_count"]
        for row in results
    ]

    assert album_counts == sorted(
        album_counts,
        reverse=True,
    )


def test_empty_search_rejected() -> None:
    with pytest.raises(ValueError):
        search_tracks("")


def test_invalid_limit_rejected() -> None:
    with pytest.raises(ValueError):
        get_top_tracks_by_genre("pop", 0)

