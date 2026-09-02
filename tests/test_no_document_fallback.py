import os

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

from types import SimpleNamespace

import backend.rag.rag_pipeline as rag_pipeline


def test_general_ai_fallback_when_no_documents_are_uploaded(monkeypatch):
    monkeypatch.setattr(rag_pipeline, "retrieve_context", lambda **kwargs: [])
    monkeypatch.setattr(rag_pipeline, "count_documents", lambda: 0)
    monkeypatch.setattr(
        rag_pipeline,
        "memory",
        SimpleNamespace(
            get_history=lambda conversation_id: [],
            add_message=lambda **kwargs: None,
        ),
    )

    def fake_generate_response(prompt):
        assert "You are a helpful general AI assistant" in prompt
        return "general answer"

    monkeypatch.setattr(rag_pipeline, "generate_response", fake_generate_response)

    result = rag_pipeline.answer_question("What is the capital of France?")

    assert result["answer"] == "general answer"
    assert result["sources"] == []


def test_document_only_mode_when_uploaded_docs_exist(monkeypatch):
    monkeypatch.setattr(rag_pipeline, "retrieve_context", lambda **kwargs: [])
    monkeypatch.setattr(rag_pipeline, "count_documents", lambda: 3)
    monkeypatch.setattr(
        rag_pipeline,
        "memory",
        SimpleNamespace(
            get_history=lambda conversation_id: [],
            add_message=lambda **kwargs: None,
        ),
    )

    def fake_generate_response(prompt):
        assert "You are a document question-answering AI assistant" in prompt
        assert "You are a helpful general AI assistant" not in prompt
        return "not found in uploaded documents"

    monkeypatch.setattr(rag_pipeline, "generate_response", fake_generate_response)

    result = rag_pipeline.answer_question("What are the frequently asked questions?")

    assert result["answer"] == "not found in uploaded documents"
    assert result["sources"] == []


def test_uploaded_documents_are_strictly_document_only_when_no_match(monkeypatch):
    monkeypatch.setattr(rag_pipeline, "retrieve_context", lambda **kwargs: [])
    monkeypatch.setattr(rag_pipeline, "count_documents", lambda: 3)
    monkeypatch.setattr(
        rag_pipeline,
        "memory",
        SimpleNamespace(
            get_history=lambda conversation_id: [],
            add_message=lambda **kwargs: None,
        ),
    )

    def fake_generate_response(prompt):
        assert "uploaded documents" in prompt
        assert "You are a helpful general AI assistant" not in prompt
        return "not found in uploaded document"

    monkeypatch.setattr(rag_pipeline, "generate_response", fake_generate_response)

    result = rag_pipeline.answer_question("What is the capital of France?")

    assert result["answer"] == "not found in uploaded document"
    assert result["sources"] == []


def test_retriever_keeps_related_internship_policy_chunks(monkeypatch):
    import backend.rag.retriever as retriever

    monkeypatch.setattr(
        retriever,
        "generate_embeddings",
        lambda texts: [[0.0] * 3 for _ in texts],
    )

    monkeypatch.setattr(
        retriever.collection,
        "count",
        lambda: 1,
    )

    monkeypatch.setattr(
        retriever.collection,
        "query",
        lambda query_embeddings, n_results, include: {
            "documents": [["Interns must complete a 2-month notice period before stipend and certificate issuance."]],
            "metadatas": [[{"source": "policy.pdf", "page": 3}]],
            "distances": [[2.3]],
        },
    )

    result = retriever.retrieve_context("internship duration", n_results=5)

    assert len(result) == 1
    assert "2-month notice period" in result[0]["text"]
    assert result[0]["source"] == "policy.pdf"


def test_sync_collection_with_files_clears_stale_data_when_no_docs_exist(monkeypatch, tmp_path):
    from backend.rag import vector_store

    calls = []

    monkeypatch.setattr(
        vector_store,
        "clear_collection",
        lambda: calls.append("cleared") or 0,
    )

    result = vector_store.sync_collection_with_files(documents_dir=tmp_path)

    assert result == 0
    assert calls == ["cleared"]
