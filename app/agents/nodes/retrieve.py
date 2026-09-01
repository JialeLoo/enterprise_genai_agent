from app.agents.state import AgentState
from app.rag.retriever import (
    retrieve_documents,
)


async def retrieve_knowledge(
    state: AgentState,
) -> dict:

    query = state["user_query"]

    documents = await retrieve_documents(
        query=query,
        top_k=4,
    )

    return {
        "retrieved_documents": documents
    }