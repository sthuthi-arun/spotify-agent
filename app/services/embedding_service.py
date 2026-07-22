from sentence_transformers import SentenceTransformer

from app.database.embedding_repository import (
    get_documents_without_embeddings,
    save_embeddings,
)


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model once and reuse it.
    """

    global _model

    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME}")

        _model = SentenceTransformer(MODEL_NAME)

    return _model


def generate_missing_embeddings(
    batch_size: int = 128,
) -> int:
    """
    Generate embeddings only for documents that do not already
    have an embedding for the selected model.
    """

    if batch_size < 1:
        raise ValueError("Batch size must be greater than zero")

    model = get_embedding_model()
    total_generated = 0

    while True:
        documents = get_documents_without_embeddings(
            model_name=MODEL_NAME,
            limit=batch_size,
        )

        if not documents:
            break

        document_texts = [
            document["document_text"]
            for document in documents
        ]

        vectors = model.encode(
            document_texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        embedding_records = [
            (
                document["track_id"],
                vector.tolist(),
            )
            for document, vector in zip(documents, vectors)
        ]

        save_embeddings(
            model_name=MODEL_NAME,
            embeddings=embedding_records,
        )

        total_generated += len(embedding_records)

        print(
            f"Generated {total_generated} embeddings so far..."
        )

    return total_generated

