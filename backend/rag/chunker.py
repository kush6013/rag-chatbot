def chunk_pages(
    pages: list[dict],
    source: str,
    chunk_size: int = 800,
    overlap: int = 150,
) -> list[dict]:

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    chunks = []

    for page in pages:
        text = page["text"]
        page_number = page["page"]

        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "text": chunk_text,
                        "source": source,
                        "page": page_number,
                    }
                )

            start += chunk_size - overlap

    return chunks
