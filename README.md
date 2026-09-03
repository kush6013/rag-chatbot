# Company Knowledge AI Chatbot

A document-grounded RAG chatbot for company knowledge and uploaded files.

## Features

- Upload PDF, TXT, and DOCX files
- Answer questions using uploaded documents only
- General fallback when no document exists
- Chat history and clear chat
- Source/reference display
- English and Hindi support
- Voice input
- Suggested questions
- Free OpenRouter model selection with fallback

## Environment Setup

1. Copy the example environment file:
   cp .env.example .env

2. Add your OpenRouter key:
   OPENROUTER_API_KEY=your_key_here

3. Optional model selection:
   OPENROUTER_MODEL=gemma
   OPENROUTER_FALLBACK_MODEL=llama

## Run locally

Backend:
  uvicorn backend.main:app --host 0.0.0.0 --port 8000

Frontend:
  python -m http.server 5500 --directory frontend

Open in browser:
  http://127.0.0.1:5500

## Docker

Build and run:
  docker build -t rag-chatbot .
  docker run -p 8000:8000 --env-file .env rag-chatbot

Or with docker-compose:
  docker-compose up --build

## Deploy on Render

1. Push this repository to GitHub.
2. In Render, select **New > Blueprint** and connect the repository.
3. Render reads `render.yaml` and creates the FastAPI web service and static frontend.
4. In the backend service's environment variables, set `OPENROUTER_API_KEY` to a valid key.
5. After the first deploy, open the frontend URL and send a test question. The backend health endpoint is available at `/health`.

The configured frontend URL and API URL use the existing Render service URLs. If you create services with different URLs, update `frontend/app.js`, `FRONTEND_URL`, and `ALLOWED_ORIGINS` to use the new frontend origin.

## Free model guidance

This project uses free OpenRouter models by default:
- gemma -> google/gemma-2-9b-it:free
- llama -> meta-llama/llama-3.1-8b-instruct:free

These are intended for free-tier usage. If a model is unavailable, the app automatically tries the second option.
