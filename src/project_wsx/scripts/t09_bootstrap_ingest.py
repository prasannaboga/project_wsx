import hashlib

from pypdf import PdfReader

from project_wsx.core.logging import logger
from project_wsx.db import SessionLocal
from project_wsx.models import Document, DocumentChunk
from project_wsx.services.ollama_client import OllamaClient
from project_wsx.services.pdf_loader import load_documents

def extract_text(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def chunk_text(text: str) -> list[str]:
    max_chars = 1200
    parts = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
    chunks: list[str] = []
    system = (
        """You are a document chunker. Split the input text into coherent, context-preserving chunks suitable for semantic search.
        - Do not break sentences or paragraphs.
        - Keep each chunk under 900 characters.
        - Preserve headings with their related content.
        - Return ONLY a JSON array of strings, where each string is a chunk."""
    )

    for part in parts:
        res = ollama_client.post(
            "/api/generate",
            {
                "model": "mistral",
                "system": system,
                "prompt": part,
                "format": "json",
                "stream": False,
            },
            timeout=90,
        )
        chunks.extend(res.get("response", []))

    return [c.strip() for c in chunks if c and c.strip()]


def embed_text(texts: list[str]) -> list[list[float]]:
    vectors: list[list[float]] = []
    for text in texts:
        res = ollama_client.post(
            "/api/embeddings",
            {"model": "nomic-embed-text", "prompt": text},
            timeout=30,
        )
        vectors.append(res["embedding"])
    return vectors


def file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    logger.info("Starting document ingestion process...")

    # ollama = OllamaClient()
    db = SessionLocal()
    
    for doc in load_documents("data/pdf_files.yml"):
        logger.info(doc)
        existing_doc = db.query(Document).filter(Document.path == doc["path"]).first()
        doc["file_hash"] = file_hash(doc["path"])
        if existing_doc and existing_doc.file_hash == doc["file_hash"]:
            logger.info(f"Already ingested and up-to-date document={doc['path']}")
            continue
        logger.info(f"Ingesting document={doc['path']}")

        if existing_doc:
            logger.info(f"Re-ingesting modified document={doc['path']}")
            db.delete(existing_doc)
            db.commit()

        extracted_text = extract_text(doc["path"])
        logger.info(f"extracted path=#{doc['path']}, length={len(extracted_text)}")

        chunks = chunk_text(extracted_text)
        vectors = embed_text(chunks)

    logger.info("Document ingestion completed successfully.")


if __name__ == "__main__":
    main()
