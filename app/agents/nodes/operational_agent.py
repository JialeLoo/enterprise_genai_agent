from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.agents.state import AgentState
from app.llm.factory import get_chat_model
from app.tools import OPERATIONAL_TOOLS


SYSTEM_PROMPT = """
You are an enterprise operations assistant.

Your job is to help users investigate deployment,
incident, service-health, and log-related questions.

Use the available tools whenever operational data
is required.

Rules:

1. Do not invent deployment details.
2. Do not invent incidents.
3. Do not invent log entries.
4. Use tools whenever the answer depends on
   enterprise operational data.
5. Use only the available tools.
6. After receiving tool results, explain the findings
   clearly and concisely.
"""


async def operational_agent(
    state: AgentState,
) -> dict:

    llm = get_chat_model()

    llm_with_tools = llm.bind_tools(
        OPERATIONAL_TOOLS
    )

    messages = state.get(
        "messages",
        [],
    )

    new_messages = []

    if not messages:

        new_messages = [
            SystemMessage(
                content=SYSTEM_PROMPT
            ),
            HumanMessage(
                content=state["user_query"]
            ),
        ]

        messages = new_messages

    response = await llm_with_tools.ainvoke(
        messages
    )

    return {
        "messages":
            new_messages + [response]
    }