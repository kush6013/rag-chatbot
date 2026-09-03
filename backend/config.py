import os

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "gemma")
OPENROUTER_FALLBACK_MODEL = os.getenv("OPENROUTER_FALLBACK_MODEL", "gemma")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# Read the deployed frontend URL from the environment (set this in Render env vars)
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://rag-frontend-q1zq.onrender.com")

# Build allowed origins list — always include local dev origins + the deployed frontend
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    f"http://127.0.0.1:5500,http://localhost:5500,http://0.0.0.0:5500,{FRONTEND_URL}",
).split(",")
