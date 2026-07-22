from app.database.embedding_repository import (
    count_documents,
    count_embeddings,
    create_embedding_tables,
    generate_track_documents,
)
from app.services.embedding_service import (
    generate_missing_embeddings,
)


def main() -> None:
    print("Step 1: Creating embedding tables...")
    create_embedding_tables()

    print("Step 2: Generating track documents...")
    generated_documents = generate_track_documents()

    print(
        f"Created or updated "
        f"{generated_documents} track documents."
    )

    print("Step 3: Generating missing embeddings...")
    generated_embeddings = generate_missing_embeddings(
        batch_size=128,
    )

    print(
        f"Generated "
        f"{generated_embeddings} new embeddings."
    )

    print("\nFinal database totals")
    print("---------------------")
    print(f"Documents: {count_documents()}")
    print(f"Embeddings: {count_embeddings()}")


if __name__ == "__main__":
    main()

