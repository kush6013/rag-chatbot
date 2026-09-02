from __future__ import annotations

from backend.rag.retriever import retrieve_context
from backend.rag.prompt import build_general_ai_prompt, build_rag_prompt
from backend.rag.vector_store import count_documents
from backend.services.llm import generate_response
from backend.services.memory import memory
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


# When True, skip external LLM calls and return extractive summaries only.
ALWAYS_EXTRACTIVE = False


def _extractive_summary(context_chunks: List[Dict[str, Any]], question: str, max_sentences: int = 4) -> List[str]:
    """
    Simple extractive summarizer: pick sentences from retrieved chunks
    that contain query tokens. If none match, fall back to the first
    sentences from the top chunks.
    """
    # Improved extractive summarizer: score sentences by token overlap
    sentences: List[str] = []
    seen = set()

    # Build token set from question (filter short tokens)
    tokens = [t for t in re.findall(r"[a-zA-Z0-9]+", question.lower()) if len(t) > 3]
    token_set = set(tokens)

    def split_sentences(text: str) -> List[str]:
        parts = re.split(r'(?<=[.!?])\s+', text.strip())
        return [p.strip() for p in parts if p.strip()]

    candidates: List[tuple[int, str]] = []

    # Collect candidate sentences and score them
    for chunk in context_chunks:
        text = chunk.get("text", "") or ""
        for s in split_sentences(text):
            low = s.lower()
            # score: number of token hits
            score = sum(1 for tok in token_set if tok in low)
            if score > 0:
                candidates.append((score, s))

    # If we have scored candidates, sort by score desc and pick top unique
    if candidates:
        candidates.sort(key=lambda x: -x[0])
        for _, sent in candidates:
            if sent not in seen:
                sentences.append(sent)
                seen.add(sent)
            if len(sentences) >= max_sentences:
                break

    # Fallback: if no sentences matched tokens, take first sentences from top chunks
    if not sentences:
        for chunk in context_chunks:
            text = chunk.get("text", "") or ""
            sents = split_sentences(text)
            for s in sents:
                if s not in seen:
                    sentences.append(s)
                    seen.add(s)
                if len(sentences) >= max_sentences:
                    break
            if len(sentences) >= max_sentences:
                break

    return sentences[:max_sentences]


def is_overview_question(question: str) -> bool:
    """
    Detect broad questions that need more context.
    """
    q = (question or "").lower().strip()
    overview_keywords = [
        "tell me about",
        "about the company",
        "about this company",
        "about this document",
        "give me an overview",
        "overview",
        "summarize",
        "summary",
        "what is this company",
        "what does the company do",
        "what is the company about",
        "describe the company",
        "describe this document",
        "main services",
        "main products",
    ]

    return any(k in q for k in overview_keywords)


def answer_question(
    question: str,
    conversation_id: str = "default",
    n_results: int = 3,
    language: str = "en",
    model_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main RAG entrypoint: retrieve relevant chunks, optionally call LLM,
    and always return answers grounded in uploaded documents when they exist.
    """

    # 1. Conversation history
    history = memory.get_history(conversation_id)
    # 2. Decide retrieval size
    retrieval_count = max(n_results, 6) if is_overview_question(question) else n_results

    # If using extractive-only mode, increase retrieval to get wider context
    if ALWAYS_EXTRACTIVE:
        retrieval_count = max(retrieval_count, 8)
    # 3. Retrieve
    context_chunks = retrieve_context(query=question, n_results=retrieval_count)

    # Deduplicate chunks by (source, page) to avoid repeating the same excerpt
    unique = []
    seen_keys = set()
    for c in context_chunks:
        key = (c.get("source"), c.get("page"))
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique.append(c)
    context_chunks = unique

    # 3b. Defensive scan if retrieval returned nothing but docs exist
    if count_documents() > 0 and not context_chunks:
        try:
            tokens = [t for t in re.findall(r"[a-zA-Z0-9]+", question.lower()) if len(t) > 3]
            scanned = []
            docs_dir = Path(__file__).resolve().parents[2] / "data" / "documents"
            if docs_dir.exists():
                for file in docs_dir.iterdir():
                    try:
                        if file.suffix.lower() == ".txt":
                            text = file.read_text(encoding="utf-8")
                            for tok in tokens:
                                if tok in text.lower():
                                    scanned.append({
                                        "text": text[:2000],
                                        "source": file.name,
                                        "page": 1,
                                        "distance": None,
                                    })
                                    break

                        if file.suffix.lower() == ".pdf":
                            try:
                                from backend.rag.loader import extract_pages_from_pdf

                                pages = extract_pages_from_pdf(str(file))
                                for page in pages:
                                    page_text = page.get("text", "") or ""
                                    for tok in tokens:
                                        if tok in page_text.lower():
                                            scanned.append({
                                                "text": page_text[:2000],
                                                "source": file.name,
                                                "page": page.get("page"),
                                                "distance": None,
                                            })
                                            break
                            except Exception:
                                continue
                    except Exception:
                        continue

            if scanned:
                context_chunks = scanned[:retrieval_count]
        except Exception:
            context_chunks = context_chunks or []

    total_documents = count_documents()

    answer: str = ""

    # If no uploaded documents, allow general assistant
    if total_documents == 0:
        prompt = build_general_ai_prompt(question=question, conversation_history=history, language=language)
        answer = generate_response(prompt)

    else:
        # Build RAG prompt (used only when calling a model)
        prompt = build_rag_prompt(question=question, context_chunks=context_chunks, conversation_history=history, language=language)

        # If configured to always use extractive summaries, skip external LLM
        if ALWAYS_EXTRACTIVE and context_chunks:
            summary_sentences = _extractive_summary(context_chunks, question, max_sentences=4)
            parts: List[str] = []
            for c in context_chunks[:3]:
                src = c.get("source", "Unknown")
                page = c.get("page", "?")
                text = (c.get("text") or "").strip()
                excerpt = (text[:500] + "...") if len(text) > 500 else text
                parts.append(f"From {src} (page {page}):\n{excerpt}")

            summary_text = "\n\n".join(f"- {s}" for s in summary_sentences) if summary_sentences else "No concise extractive summary available."

            answer = (
                "Answers are extractive-only (external LLM calls are disabled). "
                "Below is a short extractive summary pulled from the most relevant document excerpts:\n\n"
                + summary_text
                + "\n\nRelevant excerpts:\n\n"
                + "\n\n".join(parts)
            )

        else:
            # Try calling the model, but fall back to extractive summary on failure
            try:
                answer = generate_response(prompt)
            except Exception:
                answer = None

            if (answer is None or not answer) and context_chunks:
                summary_sentences = _extractive_summary(context_chunks, question, max_sentences=4)
                parts = []
                for c in context_chunks[:3]:
                    src = c.get("source", "Unknown")
                    page = c.get("page", "?")
                    text = (c.get("text") or "").strip()
                    excerpt = (text[:500] + "...") if len(text) > 500 else text
                    parts.append(f"From {src} (page {page}):\n{excerpt}")

                summary_text = "\n\n".join(f"- {s}" for s in summary_sentences) if summary_sentences else "No concise extractive summary available."

                answer = (
                    "The document retrieval system is available but the LLM provider failed. "
                    "Below is a short extractive summary pulled from the most relevant document excerpts:\n\n"
                    + summary_text
                    + "\n\nRelevant excerpts:\n\n"
                    + "\n\n".join(parts)
                )

    # Save messages to memory
    memory.add_message(conversation_id=conversation_id, role="user", content=question)
    memory.add_message(conversation_id=conversation_id, role="assistant", content=answer)

    # Prepare sources
    sources: List[Dict[str, Any]] = []
    seen = set()
    for chunk in context_chunks:
        source = chunk.get("source", "Unknown")
        page = chunk.get("page", 1)
        key = (source, page)
        if key in seen:
            continue
        seen.add(key)
        sources.append({"source": source, "page": page, "distance": chunk.get("distance")})

    return {"answer": answer, "sources": sources}
