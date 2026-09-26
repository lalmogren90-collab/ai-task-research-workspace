import hashlib
import re
from pathlib import Path

import chromadb


BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_FILE = BASE_DIR / "knowledge" / "project_knowledge.txt"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "project_knowledge"
EMBEDDING_DIMENSION = 256


def embed_text(text: str) -> list[float]:
    """Create a deterministic local embedding without external downloads."""
    vector = [0.0] * EMBEDDING_DIMENSION

    for word in re.findall(r"[a-z0-9_/.+-]+", text.lower()):
        index = int(hashlib.sha256(word.encode()).hexdigest(), 16) % EMBEDDING_DIMENSION
        vector[index] += 1.0

    norm = sum(value * value for value in vector) ** 0.5

    if norm:
        vector = [value / norm for value in vector]

    return vector


def chunk_text(text: str) -> list[str]:
    """Split the knowledge document into paragraph-based chunks."""
    return [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "AI Task & Research Workspace knowledge base"},
    )


def index_knowledge() -> int:
    text = KNOWLEDGE_FILE.read_text(encoding="utf-8")
    chunks = chunk_text(text)

    collection = get_collection()

    ids = [f"chunk-{index}" for index in range(len(chunks))]
    embeddings = [embed_text(chunk) for chunk in chunks]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=[
            {
                "source": KNOWLEDGE_FILE.name,
                "chunk": index,
            }
            for index in range(len(chunks))
        ],
    )

    return len(chunks)


def retrieve(query: str, n_results: int = 3) -> list[dict]:
    collection = get_collection()

    if collection.count() == 0:
        index_knowledge()

    result_count = min(n_results, collection.count())

    results = collection.query(
        query_embeddings=[embed_text(query)],
        n_results=result_count,
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append(
            {
                "document": document,
                "source": metadata["source"],
                "chunk": metadata["chunk"],
                "distance": round(float(distance), 4),
            }
        )

    return retrieved
