from typing import Literal, TypedDict


Intent = Literal[
    "knowledge_question",
    "operational_query",
    "general_question",
]


class AgentState(TypedDict, total=False):

    conversation_id: str

    user_query: str

    intent: Intent

    classification_confidence: float

    classification_reasoning: str

    retrieved_context: list[str]

    tool_results: list[dict]

    draft_answer: str

    final_answer: str

    error: str | None