from pathlib import Path

from backend.rag.loader import extract_pages_from_pdf
from backend.rag.chunker import chunk_pages


PDF_PATH = "data/documents/top_20_api_interview_questions.pdf"


pdf_path = Path(PDF_PATH)


def main():
    if not pdf_path.exists():
        print(f"Skipping test script: '{PDF_PATH}' does not exist.")
        return

    pages = extract_pages_from_pdf(PDF_PATH)
    print("Total pages with text:", len(pages))

    chunks = chunk_pages(
        pages=pages,
        source=pdf_path.name,
    )
    print("Total chunks:", len(chunks))

    for index, chunk in enumerate(chunks[:5], start=1):
        print("\n" + "=" * 60)
        print(f"CHUNK {index}")
        print("=" * 60)
        print("Source:", chunk["source"])
        print("Page:", chunk["page"])
        print("Text:")
        print(chunk["text"])


if __name__ == "__main__":
    main()
