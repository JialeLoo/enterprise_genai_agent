import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.state import AgentState
from app.llm.factory import get_chat_model
from app.llm.schemas import RouteDecision


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are an intent classifier for an enterprise AI assistant.

Classify the user request into exactly one of these intents:

enterprise_query:
The request requires internal enterprise knowledge or
enterprise operational information.

Examples:
- What is the production access policy?
- What is the rollback procedure?
- Why did deployment PAY-2026-0812 fail?
- Show me payment-service logs.
- Investigate this incident and tell me what our runbook says.

general_question:
The request does not require internal enterprise data.

Examples:
- Hello
- What can you do?
- Explain what an API is.

Return the structured classification only.
"""


async def classify_intent(
    state: AgentState,
) -> dict:

    query = state["user_query"]

    try:

        llm = get_chat_model()

        structured_llm = llm.with_structured_output(
            RouteDecision
        )

        decision = await structured_llm.ainvoke(
            [
                SystemMessage(
                    content=SYSTEM_PROMPT
                ),
                HumanMessage(
                    content=query
                ),
            ]
        )

        return {
            "intent": decision.intent,
            "classification_confidence":
                decision.confidence,
            "classification_reasoning":
                decision.reasoning,
        }

    except Exception as exc:

        logger.exception(
            "Intent classification failed"
        )

        return {
            "intent": "general_question",
            "classification_confidence": 0.0,
            "classification_reasoning": (
                "Classification failed. "
                "Fallback route selected."
            ),
            "error": str(exc),
        }