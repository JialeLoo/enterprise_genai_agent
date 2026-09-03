from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.agents.state import AgentState
from app.llm.factory import get_agent_model
from app.tools import ENTERPRISE_TOOLS

ENTERPRISE_PROMPT_VERSION = (
    "enterprise-agent-v1"
)

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

    llm = get_agent_model()

    llm_with_tools = llm.bind_tools(
        ENTERPRISE_TOOLS
    )

    history = list(
        state.get("messages", [])
    )

    model_messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        ),
        *history,
    ]

    last_is_current_user = (
        bool(history)
        and isinstance(
            history[-1],
            HumanMessage,
        )
        and history[-1].content
        == state["user_query"]
    )

    if not last_is_current_user:
        model_messages.append(
            HumanMessage(
                content=state["user_query"]
            )
        )

    response = await llm_with_tools.ainvoke(
        model_messages
    )

    new_messages = []

    if not last_is_current_user:
        new_messages.append(
            HumanMessage(
                content=state["user_query"]
            )
        )

    new_messages.append(response)

    return {
        "messages": new_messages
    }