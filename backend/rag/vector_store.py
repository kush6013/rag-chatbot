from pathlib import Path

import chromadb


CHROMA_PATH = "data/chroma"


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = client.get_or_create_collection(
    name="rag_documents"
)


def clear_collection():
    """
    Remove all indexed document chunks from the active collection.
    """
    all_ids = collection.get(include=[]).get("ids", [])
    if all_ids:
        collection.delete(ids=all_ids)
    return collection.count()


def sync_collection_with_files(documents_dir: str | Path):
    """
    Keep the Chroma collection aligned with the actual on-disk documents.
    If no files exist, clear the collection so stale uploaded content is not used.
    """
    documents_dir = Path(documents_dir)
    allowed_extensions = {".pdf", ".txt", ".docx"}

    files = [
        file for file in documents_dir.iterdir()
        if file.is_file() and file.suffix.lower() in allowed_extensions
    ]

    if not files:
        clear_collection()
        return 0

    existing_sources = {file.name for file in files}
    all_ids = collection.get(include=[]).get("ids", [])

    if not all_ids:
        return 0

    metadata = collection.get(include=["metadatas"]).get("metadatas", [])
    stale_ids = []

    for item, source_id in zip(metadata, all_ids):
        if not item:
            continue
        source_name = (item[0] if isinstance(item, list) else item).get("source")
        if source_name and source_name not in existing_sources:
            stale_ids.append(source_id)

    if stale_ids:
        collection.delete(ids=stale_ids)

    return collection.count()


def add_documents(
    ids: list[str],
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
):
    """
    Add document chunks and embeddings to ChromaDB.
    """

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def search_documents(
    query_embedding: list[float],
    n_results: int = 3,
):
    """
    Search ChromaDB for the most relevant chunks.
    """

    if collection.count() == 0:
        return {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(
            n_results,
            collection.count(),
        ),
    )

    return results


def delete_document(
    filename: str,
):
    """
    Delete all chunks belonging to a document.
    """

    collection.delete(
        where={
            "source": filename
        }
    )

    print(
        f"Deleted ChromaDB chunks for: {filename}"
    )


def count_documents():
    """
    Return total number of indexed chunks.
    """

    return collection.count()
