from pathlib import Path

from backend.rag.loader import extract_pages_from_pdf
from backend.rag.chunker import chunk_pages
from backend.rag.embeddings import generate_embeddings


PDF_PATH = "data/documents/top_20_api_interview_questions.pdf"


pdf_path = Path(PDF_PATH)


def main():
    if not pdf_path.exists():
        print(f"Skipping test script: '{PDF_PATH}' does not exist.")
        return

    # 1. Extract pages
    pages = extract_pages_from_pdf(PDF_PATH)
    print("Pages:", len(pages))

    # 2. Create chunks
    chunks = chunk_pages(
        pages=pages,
        source=pdf_path.name,
    )
    print("Chunks:", len(chunks))

    # 3. Extract chunk text
    texts = [chunk["text"] for chunk in chunks]

    # 4. Generate embeddings
    embeddings = generate_embeddings(texts)
    print("Embeddings:", len(embeddings))

    if embeddings:
        print("Vector dimension:", len(embeddings[0]))

    # 5. Display first chunk + embedding
    if chunks:
        print("\nFirst chunk:")
        print(chunks[0]["text"])

        print("\nMetadata:")
        print({
            "source": chunks[0]["source"],
            "page": chunks[0]["page"],
        })

        print("\nFirst 10 embedding values:")
        print(embeddings[0][:10])


if __name__ == "__main__":
    main()
