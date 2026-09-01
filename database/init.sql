CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id BIGSERIAL PRIMARY KEY,

    document_id TEXT NOT NULL,

    source TEXT NOT NULL,

    title TEXT NOT NULL,

    chunk_index INTEGER NOT NULL,

    content TEXT NOT NULL,

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    embedding VECTOR(1536) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS
knowledge_chunks_embedding_hnsw_idx
ON knowledge_chunks
USING hnsw (
    embedding vector_cosine_ops
);