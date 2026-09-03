from openai import OpenAI
import os
from pathlib import Path

from backend.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_FALLBACK_MODEL,
    OPENROUTER_MODEL,
)


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY", OPENROUTER_API_KEY)
    if (
        not api_key
        or api_key.strip().upper().startswith("REPLACE")
        or "your_openrouter" in api_key.lower()
        or "your_key" in api_key.lower()
    ):
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured or is invalid. "
            "Please set OPENROUTER_API_KEY in your environment or Render Environment Variables."
        )
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

FREE_MODELS = {
    "openrouter": "openrouter/free",
    "nemotron": "nvidia/nemotron-3.5-lightning:free",
    "gemma": "google/gemma-4-26b-a4b-it:free",
    "dots": "dots-studio/dots-3-note-preview:free",
    "liquid": "liquid/lfm-2.5-2.6b:free",
}


def _normalize_model_name(model_name: str | None) -> str:
    return (model_name or "").strip().lower().replace(" ", "")


def _resolve_model(model_name: str | None) -> str:
    normalized = _normalize_model_name(model_name)
    if not normalized:
        return FREE_MODELS["openrouter"]

    if ":" in normalized or "/" in normalized:
        return model_name.strip()

    if normalized in FREE_MODELS:
        return FREE_MODELS[normalized]

    for model in FREE_MODELS.values():
        if normalized == _normalize_model_name(model):
            return model

    return FREE_MODELS.get(normalized, FREE_MODELS["openrouter"])


def get_model_candidates(model_name: str | None) -> list[str]:
    preferred = _resolve_model(model_name or OPENROUTER_MODEL)
    fallback_model = _resolve_model(OPENROUTER_FALLBACK_MODEL)

    fallback = [
        model
        for key, model in FREE_MODELS.items()
        if model not in {preferred, fallback_model}
    ]

    if fallback_model != preferred:
        fallback.insert(0, fallback_model)

    if preferred not in fallback:
        fallback.insert(0, preferred)

    return list(dict.fromkeys(fallback))


def generate_response(message: str, model_name: str | None = None) -> str:
    client = _get_client()
    last_error = None

    for model in get_model_candidates(model_name):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful document question-answering "
                            "assistant. Answer the user's question using "
                            "the supplied document context."
                        ),
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
                max_tokens=1000,
                temperature=0.2,
                timeout=6.0,
            )

            if not response.choices:
                raise RuntimeError(
                    "OpenRouter returned no choices."
                )

            choice = response.choices[0]
            content = choice.message.content

            if content and content.strip():
                return content.strip()

            finish_reason = getattr(
                choice,
                "finish_reason",
                None,
            )

            raise RuntimeError(
                "OpenRouter returned an empty response. "
                f"finish_reason={finish_reason}"
            )

        except Exception as e:
            last_error = e
            error_text = str(e).lower()

            if (
                "402" in error_text
                or "credit" in error_text
                or "budget" in error_text
                or "rate limit" in error_text
                or "in-flight" in error_text
                or "404" in error_text
                or "no endpoints found" in error_text
                or "endpoint" in error_text and "not found" in error_text
                or "model not found" in error_text
                or "timeout" in error_text
                or "timed out" in error_text
                or "connection" in error_text
                or "504" in error_text
                or "503" in error_text
                or "502" in error_text
            ):
                continue

            raise RuntimeError(
                f"LLM request failed: {str(e)}"
            ) from e

    # If remote LLM failed, try a safe local fallback using knowledge_base files.
    def _local_fallback(msg: str) -> str:
        # Only use uploaded documents as a local fallback. Do not use any
        # backend-stored knowledge base. If no uploaded documents are present,
        # inform the user to upload a document.
        try:
            text = msg.lower()
            docs_dir = Path(__file__).resolve().parents[2] / "data" / "documents"

            if docs_dir.exists():
                tokens = [t for t in text.split() if len(t) > 3]
                for file in docs_dir.iterdir():
                    try:
                        if file.suffix.lower() == ".txt":
                            doc_text = file.read_text(encoding="utf-8").lower()
                            for tok in tokens:
                                if tok in doc_text:
                                    start = doc_text.find(tok)
                                    snippet = doc_text[max(0, start - 100): start + 400].strip()
                                    return f"(Local Docs) {file.name}: {snippet}"

                        if file.suffix.lower() == ".pdf":
                            try:
                                from backend.rag.loader import extract_pages_from_pdf
                                pages = extract_pages_from_pdf(str(file))
                                for page in pages:
                                    page_text = page.get("text", "").lower()
                                    for tok in tokens:
                                        if tok in page_text:
                                            start = page_text.find(tok)
                                            snippet = page_text[max(0, start - 100): start + 400].strip()
                                            return f"(Local Docs) {file.name} - Page {page.get('page')}: {snippet}"
                            except Exception:
                                continue
                    except Exception:
                        continue

            # No uploaded documents or no matches found
            return (
                "No uploaded documents were found or the uploaded documents do not contain the requested information. "
                "Please upload the relevant PDF or TXT file so I can answer based on it."
            )
        except Exception:
            return (
                "The AI provider is unavailable and a local fallback failed. "
                "Please try again later."
            )

    if last_error is not None:
        # Log the last error to stderr for diagnostics, then return local fallback
        try:
            print("LLM error:", str(last_error), flush=True)
        except Exception:
            pass

        return _local_fallback(message)

    # Final safety net
    return _local_fallback(message)
