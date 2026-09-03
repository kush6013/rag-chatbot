# backend/rag/embeddings.py

# Lazy import of SentenceTransformer with optional accelerate backend.
# This avoids loading heavy libraries (torch) at module import time.

from typing import List

_MODEL_NAME = "all-MiniLM-L6-v2"
_model = None  # type: ignore

def _load_model():
    """Load the SentenceTransformer model on first use.
    Uses the `accelerate` extra (ONNXRuntime) if available, otherwise falls back to CPU.
    """
    global _model
    if _model is None:
        try:
            # Import inside the function to avoid heavy imports at module load.
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is not installed. Install with \"sentence-transformers[accelerate]\""
            ) from exc
        _model = SentenceTransformer(_MODEL_NAME, device="cpu")
    return _model


def generate_embedding(text: str) -> List[float]:
    """Return a single embedding vector for *text*.
    The model is loaded lazily on first call.
    """
    model = _load_model()
    return model.encode(text, convert_to_numpy=True, normalize_embeddings=True).tolist()


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Return embeddings for a list of strings.
    The model is loaded lazily on first call.
    """
    model = _load_model()
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).tolist()
