from backend.rag.embeddings import generate_embedding
from backend.rag.vector_store import search_documents


def search(query: str, n_results: int = 3):
    query_embedding = generate_embedding(query)

    results = search_documents(
        query_embedding=query_embedding,
        n_results=n_results,
    )

    return results


if __name__ == "__main__":
    query = "What is a REST API?"

    results = search(query)

    print("\nSearch query:")
    print(query)

    print("\nResults:")

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for index, document in enumerate(documents):
        print("\n" + "=" * 60)
        print(f"RESULT {index + 1}")
        print("=" * 60)

        print("Source:", metadatas[index]["source"])
        print("Page:", metadatas[index]["page"])
        print("Distance:", distances[index])

        print("\nText:")
        print(document)
