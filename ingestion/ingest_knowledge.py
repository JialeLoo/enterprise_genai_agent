import hashlib
from pathlib import Path

from app.llm.embeddings import (
    get_embedding_model,
)
from app.rag.chunking import chunk_text
from app.rag.repository import upsert_chunk


KNOWLEDGE_DIR = Path("knowledge")


def create_document_id(
    path: Path,
) -> str:

    return hashlib.sha256(
        str(path).encode()
    ).hexdigest()[:16]


def extract_title(
    text: str,
    fallback: str,
) -> str:

    for line in text.splitlines():

        line = line.strip()

        if line.startswith("# "):
            return line.removeprefix("# ").strip()

    return fallback


def ingest_document(
    path: Path,
) -> None:

    print(f"Ingesting {path}")

    text = path.read_text(
        encoding="utf-8"
    )

    title = extract_title(
        text,
        path.stem,
    )

    chunks = chunk_text(text)

    embedding_model = (
        get_embedding_model()
    )

    embeddings = (
        embedding_model.embed_documents(
            chunks
        )
    )

    document_id = create_document_id(
        path
    )

    for index, (
        chunk,
        embedding,
    ) in enumerate(
        zip(
            chunks,
            embeddings,
        )
    ):

        upsert_chunk(
            document_id=document_id,
            source=str(path),
            title=title,
            chunk_index=index,
            content=chunk,
            metadata={
                "filename": path.name,
                "document_type": "internal_knowledge",
            },
            embedding=embedding,
        )

    print(
        f"Inserted {len(chunks)} chunks"
    )


def main():

    documents = list(
        KNOWLEDGE_DIR.glob("*.md")
    )

    for document in documents:
        ingest_document(document)


if __name__ == "__main__":
    main()