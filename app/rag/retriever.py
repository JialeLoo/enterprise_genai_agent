from app.llm.embeddings import (
    get_embedding_model,
)

from app.rag.repository import (
    search_chunks,
)


async def retrieve_documents(
    query: str,
    top_k: int = 4,
    min_similarity: float = 0.55,
) -> list[dict]:

    embedding_model = (
        get_embedding_model()
    )

    query_embedding = (
        await embedding_model.aembed_query(
            query
        )
    )

    results = search_chunks(
        query_embedding=query_embedding,
        limit=top_k,
    )

    return [
        result
        for result in results
        if result["similarity"]
        >= min_similarity
    ]