from pprint import pprint

from app.database.repository import (
    get_top_tracks_by_genre,
    rank_artists_by_album_count,
    search_tracks,
)

from app.database.repository import (
    get_track_by_id,
    recommend_similar_tracks,
)


def test_recommendations() -> None:
    search_results = search_tracks("love", limit=1)

    if not search_results:
        print("No test track found")
        return

    track_id = search_results[0]["track_id"]

    selected_track = get_track_by_id(track_id)
    recommendations = recommend_similar_tracks(
        track_id=track_id,
        limit=5,
    )

    print("\nSelected track:")
    print(selected_track)

    print("\nRecommendations:")
    for recommendation in recommendations:
        print(recommendation)

def main() -> None:
#    print("\nTop pop tracks:")
 #   pprint(get_top_tracks_by_genre("pop", 3))

#    print("\nSearch results:")
 #   pprint(search_tracks("weeknd", 5))

  #  print("\nArtists ranked by album count:")
   # pprint(rank_artists_by_album_count(10))
    
    test_recommendations()


if __name__ == "__main__":
    main()
    

