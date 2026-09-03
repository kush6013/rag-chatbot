import re

from backend.rag.vector_store import collection
from backend.rag.embeddings import generate_embeddings


# --------------------------------
# Retrieval settings
# --------------------------------

# We don't want to reject useful chunks too aggressively.
# Chroma distance depends on the embedding/model configuration,
# and some policy questions are phrased differently from the exact text
# used in the document.
RELEVANCE_THRESHOLD = 1.40
RELEVANCE_SOFT_THRESHOLD = 2.50


def _stem_word(word: str) -> str:
    """Keep a small stem for common English forms and policy terms."""
    w = word.lower().strip()
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("sses") and len(w) > 5:
        return w[:-2]
    if w.endswith("s") and len(w) > 3 and not w.endswith("ss"):
        return w[:-1]
    if w.endswith("ing") and len(w) > 5:
        return w[:-3]
    if w.endswith("ed") and len(w) > 4:
        return w[:-2]
    return w


def _expand_keywords(text: str) -> set[str]:
    synonyms = {
        "internship": {"intern", "interns", "trainee", "trainees"},
        "duration": {"duration", "time", "period", "length", "month", "months"},
        "leave": {"leave", "absence", "vacation", "timeoff", "holiday"},
        "company": {"company", "organization", "organisation", "firm"},
        "service": {"service", "services", "product", "products"},
        "policy": {"policy", "policies", "rule", "rules"},
    }

    result: set[str] = set()
    for token in re.findall(r"[a-zA-Z0-9]+", text):
        if len(token) <= 2:
            continue
        word = token.lower()
        stem = _stem_word(word)
        result.add(word)
        result.add(stem)
        for key, values in synonyms.items():
            if word == key or stem == key:
                result.update(values)
            if word in values or stem in values:
                result.add(key)
                result.add(word)
                result.add(stem)
    return result


def _has_keyword_overlap(document: str, query: str) -> bool:
    """Return True if the document text shares meaningful words with the query."""
    document_keywords = _expand_keywords(document)
    query_keywords = _expand_keywords(query)
    return bool(document_keywords & query_keywords)


def retrieve_context(
    query: str,
    n_results: int = 5,
):
    """
    Retrieve relevant document chunks from ChromaDB.

    Works for both:
    - specific questions
    - broad/overview questions
    """

    if not query or not query.strip():
        return []

    # --------------------------------
    # Check whether knowledge base
    # contains documents
    # --------------------------------

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    # Don't request more chunks than exist.
    search_count = min(
        n_results,
        total_chunks,
    )

    # --------------------------------
    # Generate query embedding
    # --------------------------------

    query_embedding = generate_embeddings(
        [query.strip()]
    )[0]

    # --------------------------------
    # Search ChromaDB
    # --------------------------------

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=search_count,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents = results.get(
        "documents",
        [[]],
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]],
    )[0]

    distances = results.get(
        "distances",
        [[]],
    )[0]

    # --------------------------------
    # Build context
    # --------------------------------
    context = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):

        # Skip empty chunks
        if not document or not document.strip():
            continue

        # Accept chunks that either pass the semantic threshold or share
        # enough meaningful keywords with the user's question.
        is_relevant = (
            distance <= RELEVANCE_THRESHOLD
            or (
                distance <= RELEVANCE_SOFT_THRESHOLD
                and _has_keyword_overlap(document, query)
            )
        )

        if not is_relevant:
            continue

        metadata = metadata or {}

        context.append(
            {
                "text": document,
                "source": metadata.get(
                    "source",
                    "Unknown",
                ),
                "page": metadata.get(
                    "page",
                    "Unknown",
                ),
                "distance": distance,
            }
        )

    # If uploaded documents exist on disk, prefer context chunks whose
    # source matches files in data/documents. This prevents returning
    # backend-stored knowledge_base results when user-uploaded docs are present.
    try:
        from pathlib import Path

        docs_dir = Path(__file__).resolve().parents[2] / "data" / "documents"
        docs_files = {p.name for p in docs_dir.iterdir() if p.is_file()} if docs_dir.exists() else set()

        if docs_files:
            preferred = [c for c in context if c.get("source") in docs_files]
            others = [c for c in context if c.get("source") not in docs_files]
            # return up to n_results, preferring uploaded docs
            merged = preferred + others
            return merged[:n_results]
    except Exception:
        pass

    return context[:n_results]
