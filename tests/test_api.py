from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200


def test_docs_endpoint():
    response = client.get("/docs")

    assert response.status_code == 200


def test_search_endpoint():
    response = client.get(
        "/search",
        params={
            "query": "calm acoustic music",
            "limit": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert "results" in data
    assert "result_count" in data
    assert isinstance(data["results"], list)
    assert data["result_count"] == len(data["results"])
    assert data["result_count"] <= 3

def test_agent_endpoint():
    response = client.post(
        "/agent",
        json={
            "query": "find calm acoustic music",
            "limit": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "find calm acoustic music"
    assert data["intent"] == "search_tracks"
    assert data["result_count"] <= 3
    assert isinstance(data["results"], list)


def test_agent_recommendation_endpoint():
    response = client.post(
        "/agent",
        json={
            "query": (
                "recommend songs similar to Shape of You"
            ),
            "limit": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "recommend_tracks"
    assert data["result_count"] <= 3


def test_agent_rejects_empty_query():
    response = client.post(
        "/agent",
        json={
            "query": " ",
            "limit": 5,
        },
    )

    assert response.status_code == 422


def test_agent_rejects_large_limit():
    response = client.post(
        "/agent",
        json={
            "query": "find rock music",
            "limit": 100,
        },
    )

    assert response.status_code == 422

