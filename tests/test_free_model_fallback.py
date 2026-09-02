from backend.services.llm import get_model_candidates


def test_get_model_candidates_uses_current_free_model_names():
    candidates = get_model_candidates("gemma")

    assert "google/gemma-3-12b-it:free" in candidates
    assert "google/gemma-2-9b-it:free" not in candidates
