from typing import Any


def safe_value(
    value: Any,
    default: str = "unknown",
) -> str:
    """
    Convert missing or empty values into readable document text.
    """

    if value is None:
        return default

    text = str(value).strip()

    if not text:
        return default

    return text


def build_track_document(
    track: dict[str, Any],
) -> str:
    """
    Convert one structured track record into natural-language text.

    The embedding model converts this document into a numeric vector.
    """

    return (
        f"Track: {safe_value(track.get('track_name'))}. "
        f"Artist: {safe_value(track.get('artists'))}. "
        f"Album: {safe_value(track.get('album_name'))}. "
        f"Genre: {safe_value(track.get('track_genre'))}. "
        f"Popularity score: {safe_value(track.get('popularity'))}. "
        f"Danceability: {safe_value(track.get('danceability'))}. "
        f"Energy: {safe_value(track.get('energy'))}. "
        f"Acousticness: {safe_value(track.get('acousticness'))}. "
        f"Instrumentalness: "
        f"{safe_value(track.get('instrumentalness'))}. "
        f"Valence: {safe_value(track.get('valence'))}. "
        f"Tempo: {safe_value(track.get('tempo'))} BPM."
    )
