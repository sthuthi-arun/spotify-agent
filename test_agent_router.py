from app.services.agent_router import classify_agent_request


def main() -> None:
    requests = [
        "Find 5 calm acoustic songs",
        "Recommend 10 tracks similar to Blinding Lights",
        "Show me the top 8 artists with the most albums",
        "Which tracks have the highest energy?",
        "What can you do?",
        "Book me a flight to Japan",
    ]

    for request in requests:
        plan = classify_agent_request(request)

        print("=" * 70)
        print(f"Request: {request}")
        print(f"Intent: {plan.intent.value}")
        print(f"Search query: {plan.search_query}")
        print(f"Limit: {plan.limit}")
        print(f"Reason: {plan.explanation}")


if __name__ == "__main__":
    main()
