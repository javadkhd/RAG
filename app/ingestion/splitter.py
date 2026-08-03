from app.ingestion.cleaner import clean as _clean


def split(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    cleaned = _clean(text)
    tokens = cleaned.split()
    if not tokens:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(" ".join(chunk_tokens))
        start += chunk_size - overlap

    return chunks
