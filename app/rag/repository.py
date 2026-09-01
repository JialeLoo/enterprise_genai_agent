import json

from pgvector.psycopg import register_vector

from app.database.postgres import (
    get_connection,
)


def upsert_chunk(
    *,
    document_id: str,
    source: str,
    title: str,
    chunk_index: int,
    content: str,
    metadata: dict,
    embedding: list[float],
) -> None:

    with get_connection() as conn:

        register_vector(conn)

        with conn.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO knowledge_chunks (
                    document_id,
                    source,
                    title,
                    chunk_index,
                    content,
                    metadata,
                    embedding
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                ON CONFLICT (
                    document_id,
                    chunk_index
                )
                DO UPDATE SET
                    source = EXCLUDED.source,
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    embedding = EXCLUDED.embedding
                """,
                (
                    document_id,
                    source,
                    title,
                    chunk_index,
                    content,
                    json.dumps(metadata),
                    embedding,
                ),
            )


def search_chunks(
    *,
    query_embedding: list[float],
    limit: int = 4,
) -> list[dict]:

    with get_connection() as conn:

        register_vector(conn)

        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    document_id,
                    source,
                    title,
                    chunk_index,
                    content,
                    metadata,
                    1 - (
                        embedding <=> %s
                    ) AS similarity
                FROM knowledge_chunks
                ORDER BY
                    embedding <=> %s
                LIMIT %s
                """,
                (
                    query_embedding,
                    query_embedding,
                    limit,
                ),
            )

            rows = cursor.fetchall()

    results = []

    for row in rows:

        results.append(
            {
                "id": row[0],
                "document_id": row[1],
                "source": row[2],
                "title": row[3],
                "chunk_index": row[4],
                "content": row[5],
                "metadata": row[6],
                "similarity": float(
                    row[7]
                ),
            }
        )

    return results