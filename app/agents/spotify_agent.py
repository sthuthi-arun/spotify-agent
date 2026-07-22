from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from app.services.semantic_search import semantic_search_tracks


Intent = Literal[
    "semantic_search",
    "recommendation",
    "unknown",
]


class SpotifyAgentState(TypedDict, total=False):
    query: str
    limit: int
    intent: Intent
    results: list[dict[str, Any]]
    message: str


def classify_intent(
    state: SpotifyAgentState,
) -> dict[str, Intent]:
    query = state["query"].lower()

    recommendation_terms = (
        "recommend",
        "suggest",
        "similar",
        "playlist",
        "songs like",
        "music like",
    )

    if any(term in query for term in recommendation_terms):
        return {"intent": "recommendation"}

    return {"intent": "semantic_search"}


def run_semantic_search(
    state: SpotifyAgentState,
) -> dict[str, Any]:
    results = semantic_search_tracks(
        query=state["query"],
        limit=state.get("limit", 10),
    )

    return {
        "results": results,
        "message": f"Found {len(results)} matching tracks.",
    }


def run_recommendation(
    state: SpotifyAgentState,
) -> dict[str, Any]:
    results = semantic_search_tracks(
        query=state["query"],
        limit=state.get("limit", 10),
    )

    return {
        "results": results,
        "message": f"Generated {len(results)} recommendations.",
    }


def select_route(
    state: SpotifyAgentState,
) -> Intent:
    return state.get("intent", "unknown")


def build_spotify_agent():
    graph = StateGraph(SpotifyAgentState)

    graph.add_node(
        "classify_intent",
        classify_intent,
    )
    graph.add_node(
        "semantic_search",
        run_semantic_search,
    )
    graph.add_node(
        "recommendation",
        run_recommendation,
    )

    graph.add_edge(
        START,
        "classify_intent",
    )

    graph.add_conditional_edges(
        "classify_intent",
        select_route,
        {
            "semantic_search": "semantic_search",
            "recommendation": "recommendation",
            "unknown": "semantic_search",
        },
    )

    graph.add_edge(
        "semantic_search",
        END,
    )
    graph.add_edge(
        "recommendation",
        END,
    )

    return graph.compile()


spotify_agent = build_spotify_agent()
