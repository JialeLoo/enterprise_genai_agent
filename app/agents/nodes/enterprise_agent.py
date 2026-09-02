from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.agents.state import AgentState
from app.llm.factory import get_chat_model
from app.tools import ENTERPRISE_TOOLS


SYSTEM_PROMPT = """
You are an enterprise AI assistant.

You help users investigate operational issues and answer
questions about internal enterprise knowledge.

You have access to tools for:

- deployment information
- incidents
- service logs
- internal documentation and runbooks

Use tools whenever the answer depends on enterprise data.

Important rules:

1. Do not invent deployment details.
2. Do not invent incidents or logs.
3. Do not invent internal policies or procedures.
4. Use search_knowledge when the user asks about internal
   policies, procedures, guidelines or runbooks.
5. Use operational tools when the user asks about live or
   historical operational system state.
6. You may use multiple tools when necessary.
7. If tool results are insufficient, say so.
8. Clearly distinguish observed operational facts from
   documented procedural guidance.
"""


async def enterprise_agent(
    state: AgentState,
) -> dict:

    llm = get_chat_model()

    llm_with_tools = llm.bind_tools(
        ENTERPRISE_TOOLS
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