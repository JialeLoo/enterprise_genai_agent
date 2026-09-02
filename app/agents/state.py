from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


Intent = Literal[
    "enterprise_query",
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

    final_answer: str
    error: str | None

    classifier_provider: str
    classifier_model: str

    agent_provider: str
    agent_model: str