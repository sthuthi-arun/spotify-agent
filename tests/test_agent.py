import pytest

from app.agents.spotify_agent import (
    classify_intent,
    clean_query,
    extract_recommendation_track_name,
    remove_duplicate_tracks,
    run_agent,
)
from app.models.agent_models import AgentIntent


def test_clean_query_removes_extra_spaces():
    result = clean_query(
        "  find   calm   acoustic   music  "
    )

    assert result == "find calm acoustic music"


def test_classify_search_intent():
    plan = classify_intent(
        "find calm acoustic music"
    )

    assert plan.intent == AgentIntent.SEARCH_TRACKS


def test_classify_recommendation_intent():
    plan = classify_intent(
        "recommend songs similar to Shape of You"
    )

    assert plan.intent == AgentIntent.RECOMMEND_TRACKS


def test_classify_artist_analytics_intent():
    plan = classify_intent(
        "show artists with the most albums"
    )

    assert plan.intent == AgentIntent.ARTIST_ANALYTICS


def test_classify_track_analytics_intent():
    plan = classify_intent(
        "show the most popular tracks"
    )

    assert plan.intent == AgentIntent.TRACK_ANALYTICS


def test_extract_recommendation_track_name():
    track_name = extract_recommendation_track_name(
        "recommend songs similar to Shape of You"
    )

    assert track_name == "Shape of You"


def test_remove_duplicate_tracks_by_track_id():
    results = [
        {
            "track_id": "1",
            "track_name": "Song A",
            "artists": "Artist A",
        },
        {
            "track_id": "1",
            "track_name": "Song A",
            "artists": "Artist A",
        },
        {
            "track_id": "2",
            "track_name": "Song B",
            "artists": "Artist B",
        },
    ]

    cleaned = remove_duplicate_tracks(results)

    assert len(cleaned) == 2


def test_remove_duplicate_tracks_without_track_id():
    results = [
        {
            "track_name": "Song A",
            "artists": "Artist A",
        },
        {
            "track_name": "song a",
            "artists": "artist a",
        },
    ]

    cleaned = remove_duplicate_tracks(results)

    assert len(cleaned) == 1


def test_run_agent_search():
    response = run_agent(
        query="find calm acoustic music",
        limit=3,
    )

    assert response.intent == AgentIntent.SEARCH_TRACKS
    assert response.result_count <= 3
    assert isinstance(response.results, list)


def test_run_agent_rejects_short_query():
    with pytest.raises(ValueError):
        run_agent(
            query=" ",
            limit=5,
        )


def test_run_agent_rejects_invalid_limit():
    with pytest.raises(ValueError):
        run_agent(
            query="find rock music",
            limit=100,
        )
