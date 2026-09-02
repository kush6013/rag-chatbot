from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.rag.index_documents import index_file
from backend.rag.vector_store import collection, sync_collection_with_files


router = APIRouter()

DOCUMENTS_DIR = Path("data/documents")

DOCUMENTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
}


@router.get("/")
def list_documents():
    """
    Return all documents currently in the knowledge base.
    """

    documents = []

    for file in sorted(DOCUMENTS_DIR.iterdir()):

        if (
            file.is_file()
            and file.suffix.lower()
            in ALLOWED_EXTENSIONS
        ):

            documents.append(
                {
                    "filename": file.name,
                    "type": file.suffix.lower().replace(
                        ".",
                        ""
                    ),
                    "size": file.stat().st_size,
                }
            )

    if not documents:
        sync_collection_with_files(DOCUMENTS_DIR)

    return {
        "documents": documents,
        "count": len(documents),
        "indexed_chunks": collection.count(),
    }


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    """
    Upload and index a PDF, TXT, or DOCX document.
    """

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected.",
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Allowed: PDF, TXT, DOCX."
            ),
        )

    safe_filename = Path(
        file.filename
    ).name

    file_path = (
        DOCUMENTS_DIR /
        safe_filename
    )

    try:

        contents = await file.read()

        if not contents:

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        # Save document

        with open(
            file_path,
            "wb",
        ) as buffer:

            buffer.write(contents)

        print(
            f"Uploaded: {file_path}"
        )

        # Index document

        result = index_file(
            str(file_path)
        )

        return {
            "message": (
                "Document uploaded and "
                "indexed successfully."
            ),
            **result,
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            f"Upload error: {e}"
        )

        # Remove partially processed file

        if file_path.exists():

            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document processing failed: {str(e)}"
            ),
        )


@router.delete("/{filename}")
def delete_document(
    filename: str
):
    """
    Delete a document from the knowledge base.
    """

    safe_filename = Path(
        filename
    ).name

    file_path = (
        DOCUMENTS_DIR /
        safe_filename
    )

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    try:

        file_path.unlink()
        sync_collection_with_files(DOCUMENTS_DIR)

        return {
            "message": (
                f"{safe_filename} deleted successfully."
            ),
            "filename": safe_filename,
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}",
        )
