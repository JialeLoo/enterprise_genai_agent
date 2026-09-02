from langchain_core.tools import tool

from app.rag.retriever import retrieve_documents


@tool
async def search_knowledge(
    query: str,
) -> list[dict]:
    """
    Search internal enterprise documentation.

    Use this when the user asks about policies,
    procedures, runbooks, guidelines, access rules,
    incident response procedures, deployment procedures,
    or other internal knowledge.
    """

    return await retrieve_documents(
        query=query,
        top_k=4,
        min_similarity=0.55,
    )