from backend.services.llm import get_model_candidates


def test_get_model_candidates_uses_current_free_model_names():
    candidates = get_model_candidates("openrouter")

    assert "openrouter/free" in candidates


