import hashlib
import re

from pypdf import PdfReader

from project_wsx.core.logging import logger
from project_wsx.db import SessionLocal
from project_wsx.models import Document, DocumentChunk
from project_wsx.services import ollama_client
from project_wsx.services.ollama_client import OllamaClient
from project_wsx.services.pdf_loader import load_documents


def embed_chunks(chunks: list[str], ollama_client: OllamaClient) -> list[list[float]]:
    logger.info(f"Embedding {len(chunks)} chunks")

    vectors: list[list[float]] = []

    for i, chunk in enumerate(chunks):
        res = ollama_client.post(
            "/api/embeddings",
            {
                "model": "nomic-embed-text",
                "prompt": chunk,
            },
            timeout=30,
        )
        vectors.append(res["embedding"])

    logger.info(
        f"Embedding completed: count={len(vectors)}, dim={len(vectors[0]) if vectors else 0}"
    )
    return vectors

def is_table_block(text: str) -> bool:
    lines = text.strip().splitlines()
    if len(lines) < 2:
        return False

    numeric_lines = sum(1 for line in lines if re.search(r"\d", line))

    aligned_spacing = sum(1 for line in lines if re.search(r"\s{2,}", line))

    separators = any(re.match(r"^[\-\_=|]+$", line.strip()) for line in lines)

    return (
        numeric_lines >= len(lines) * 0.5 and aligned_spacing >= len(lines) * 0.5
    ) or separators


def chunk_text(
    text: str,
    max_chars: int = 900,
) -> list[str]:
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    chunks: list[str] = []

    current: list[str] = []
    current_len = 0

    for block in blocks:
        block_len = len(block)

        # If this block is a table, flush current chunk first
        if is_table_block(block):
            if current:
                chunks.append("\n\n".join(current))
                current = []
                current_len = 0

            chunks.append(block)
            continue

        # Normal paragraph handling
        if current_len + block_len > max_chars:
            if current:
                chunks.append("\n\n".join(current))
                current = []
                current_len = 0

        current.append(block)
        current_len += block_len

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def extract_text(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def main():
    logger.info("Starting document ingestion process...")

    db = SessionLocal()
    ollama_client = OllamaClient()

    for doc in load_documents("data/pdf_files.yml"):
        logger.info(doc)
        extracted_text = extract_text(doc["path"])
        logger.info(f"extracted path={doc['path']}, length={len(extracted_text)}")

        chunk_texts_list = chunk_text(extracted_text)
        vectors = embed_chunks(chunk_texts_list, ollama_client)
    logger.info("Document ingestion completed successfully.")


if __name__ == "__main__":
    main()
