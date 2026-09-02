import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.chat import router as chat_router
from backend.api.documents import router as documents_router
from backend.config import ALLOWED_ORIGINS


app = FastAPI(
    title="RAG Chatbot API",
    version="1.0.0",
)


origins = [origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    chat_router,
    prefix="/api",
)


app.include_router(
    documents_router,
    prefix="/api/documents",
)


@app.get("/")
def root():
    return {
        "message": "RAG Chatbot API is running"
    }


@app.get("/health")
def health():
    from backend.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
    ok = bool(OPENROUTER_API_KEY and not OPENROUTER_API_KEY.strip().upper().startswith("REPLACE"))
    return {
        "status": "ok" if ok else "unhealthy",
        "openrouter_api_key_present": ok,
        "active_model": OPENROUTER_MODEL,
    }
