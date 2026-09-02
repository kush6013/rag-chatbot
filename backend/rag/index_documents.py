from pathlib import Path

from docx import Document

from backend.rag.loader import extract_pages_from_pdf
from backend.rag.chunker import chunk_pages
from backend.rag.embeddings import generate_embeddings
from backend.rag.vector_store import add_documents, clear_collection


def extract_text_from_txt(file_path: Path):
    text = file_path.read_text(
        encoding="utf-8"
    )

    return [
        {
            "text": text,
            "page": 1,
        }
    ]


def extract_text_from_docx(file_path: Path):
    document = Document(
        str(file_path)
    )

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    )

    return [
        {
            "text": text,
            "page": 1,
        }
    ]


def extract_document(file_path: Path):
    extension = file_path.suffix.lower()

    if extension == ".pdf":

        return extract_pages_from_pdf(
            str(file_path)
        )

    if extension == ".txt":

        return extract_text_from_txt(
            file_path
        )

    if extension == ".docx":

        return extract_text_from_docx(
            file_path
        )

    raise ValueError(
        "Unsupported file type. "
        "Supported: PDF, TXT, DOCX."
    )


def index_file(file_path: str):

    file = Path(file_path)

    if not file.exists():
        raise FileNotFoundError(
            f"Document not found: {file}"
        )

    print(
        f"Processing: {file.name}"
    )

    # -----------------------------
    # 0. Reset the active collection
    #    so only the newest uploaded
    #    document is used as knowledge.
    # -----------------------------

    clear_collection()

    # -----------------------------
    # 1. Extract text
    # -----------------------------

    pages = extract_document(file)

    print(
        f"Pages extracted: {len(pages)}"
    )

    if not pages:
        raise ValueError(
            "No text could be extracted."
        )

    # -----------------------------
    # 2. Chunk text
    # -----------------------------

    chunks = chunk_pages(
        pages=pages,
        source=file.name,
    )

    print(
        f"Chunks created: {len(chunks)}"
    )

    if not chunks:
        raise ValueError(
            "No chunks were created."
        )

    # -----------------------------
    # 3. Prepare texts
    # -----------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    # -----------------------------
    # 4. Generate embeddings
    # -----------------------------

    print(
        "Generating embeddings..."
    )

    embeddings = generate_embeddings(
        texts
    )

    print(
        f"Embeddings generated: "
        f"{len(embeddings)}"
    )

    # -----------------------------
    # 5. Create unique IDs
    # -----------------------------

    ids = [
        f"{file.stem}_chunk_{index}"
        for index in range(
            len(chunks)
        )
    ]

    # -----------------------------
    # 6. Metadata
    # -----------------------------

    metadatas = [
        {
            "source": chunk["source"],
            "page": chunk["page"],
        }
        for chunk in chunks
    ]

    # -----------------------------
    # 7. Store in ChromaDB
    # -----------------------------

    add_documents(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(
        f"Successfully indexed: "
        f"{file.name}"
    )

    return {
        "filename": file.name,
        "pages": len(pages),
        "chunks": len(chunks),
    }
