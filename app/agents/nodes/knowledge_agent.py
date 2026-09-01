from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.agents.state import AgentState
from app.llm.factory import get_chat_model


SYSTEM_PROMPT = """
You are an enterprise knowledge assistant.

Answer the user's question using only the retrieved
internal knowledge provided to you.

Rules:

1. Do not invent company policies or procedures.
2. If the retrieved information does not answer the
   question, say that the available documentation is
   insufficient.
3. Prefer precise answers over speculation.
4. Cite the supplied source numbers in your answer,
   for example [1] or [2].
"""


async def generate_knowledge_answer(
    state: AgentState,
) -> dict:

    query = state["user_query"]

    documents = state.get(
        "retrieved_documents",
        [],
    )

    if not documents:

        return {
            "final_answer": (
                "I could not find relevant internal "
                "documentation for this request."
            )
        }

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        context_parts.append(
            f"""
SOURCE [{index}]
Title: {document['title']}
Source: {document['source']}

{document['content']}
"""
        )

    context = "\n".join(
        context_parts
    )

    llm = get_chat_model()

    response = await llm.ainvoke(
        [
            SystemMessage(
                content=SYSTEM_PROMPT
            ),
            HumanMessage(
                content=f"""
User question:

{query}

Retrieved internal knowledge:

{context}
"""
            ),
        ]
    )

    return {
        "final_answer":
            str(response.content)
    }