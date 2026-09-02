import pymupdf


def extract_pages_from_pdf(pdf_path: str) -> list[dict]:
    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        page_text = page.get_text().strip()

        if page_text:
            pages.append(
                {
                    "page": page_number,
                    "text": page_text,
                }
            )

    document.close()

    return pages
