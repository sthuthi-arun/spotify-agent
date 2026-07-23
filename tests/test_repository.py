import pytest

from app.database.repository import (
    find_track_by_name,
    get_track_by_id,
    rank_artists_by_album_count,
    recommend_similar_tracks,
)


def test_find_track_by_name_returns_track():
    track = find_track_by_name("Shape of You")

    assert track is not None
    assert "track_id" in track
    assert "track_name" in track
    assert "artists" in track


def test_find_track_by_name_returns_none_for_missing_track():
    track = find_track_by_name(
        "this-track-definitely-does-not-exist-xyz"
    )

    assert track is None


def test_find_track_by_name_rejects_empty_name():
    with pytest.raises(ValueError):
        find_track_by_name("   ")


def test_get_track_by_id_returns_track():
    selected_track = find_track_by_name("Shape of You")

    assert selected_track is not None

    track = get_track_by_id(selected_track["track_id"])

    assert track is not None
    assert track["track_id"] == selected_track["track_id"]


def test_rank_artists_by_album_count_respects_limit():
    results = rank_artists_by_album_count(limit=5)

    assert isinstance(results, list)
    assert len(results) <= 5

    if results:
        assert "artists" in results[0]
        assert "album_count" in results[0]


def test_rank_artists_rejects_invalid_limit():
    with pytest.raises(ValueError):
        rank_artists_by_album_count(limit=0)


def test_recommend_similar_tracks_returns_results():
    selected_track = find_track_by_name("Shape of You")

    assert selected_track is not None

    results = recommend_similar_tracks(
        track_id=selected_track["track_id"],
        limit=5,
    )

    assert isinstance(results, list)
    assert len(results) <= 5


def test_recommend_similar_tracks_rejects_invalid_limit():
    with pytest.raises(ValueError):
        recommend_similar_tracks(
            track_id="example-track-id",
            limit=0,
        )
