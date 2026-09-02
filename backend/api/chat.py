from fastapi import APIRouter, HTTPException

from backend.schemas import (
    ChatRequest,
    ChatResponse,
)

from backend.rag.rag_pipeline import (
    answer_question,
)
from backend.rag.vector_store import clear_collection
from backend.services.memory import memory


router = APIRouter()


@router.get("/chat/history")
def get_chat_history():
    return {
        "conversations": memory.list_conversations(),
    }


@router.delete("/chat/{conversation_id}")
def delete_chat_history(conversation_id: str):
    try:
        memory.clear(conversation_id)
        clear_collection()

        documents_dir = "data/documents"
        import os

        if os.path.isdir(documents_dir):
            for file_name in os.listdir(documents_dir):
                file_path = os.path.join(documents_dir, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        return {
            "message": "Chat cleared and uploaded documents removed.",
            "conversation_id": conversation_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear chat: {str(e)}",
        )


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    try:

        result = answer_question(
            question=request.message,
            conversation_id=request.conversation_id,
            n_results=3,
            language=request.language,
            model_name=request.model,
        )

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
        )

    except Exception as e:
        error_text = str(e).lower()

        if (
            "402" in error_text
            or "credit" in error_text
            or "budget" in error_text
            or "in-flight" in error_text
        ):
            raise HTTPException(
                status_code=402,
                detail=(
                    "OpenRouter credit limit reached. Please wait a few minutes "
                    "or add credits to continue."
                ),
            )

        raise HTTPException(
            status_code=500,
            detail=(
                f"RAG request failed: {str(e)}"
            ),
        )
