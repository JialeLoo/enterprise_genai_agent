from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


Intent = Literal[
    "knowledge_question",
    "operational_query",
    "general_question",
]


class AgentState(TypedDict, total=False):

    conversation_id: str

    user_query: str

    messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

    intent: Intent

    classification_confidence: float

    classification_reasoning: str

    retrieved_documents: list[dict]

    draft_answer: str

    final_answer: str

    error: str | None