from typing import Literal

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from langgraph.prebuilt import ToolNode

from app.agents.state import AgentState

from app.agents.nodes.classify import (
    classify_intent,
)

from app.agents.nodes.enterprise_agent import (
    enterprise_agent,
)

from app.agents.nodes.general import (
    handle_general_question,
)

from app.agents.nodes.respond import (
    generate_final_response,
)

from app.tools import ENTERPRISE_TOOLS


tool_node = ToolNode(
    ENTERPRISE_TOOLS
)


def route_by_intent(
    state: AgentState,
) -> Literal[
    "enterprise_agent",
    "general",
]:

    confidence = state.get(
        "classification_confidence",
        0.0,
    )

    if confidence < 0.65:
        return "general"

    if state["intent"] == "enterprise_query":
        return "enterprise_agent"

    return "general"


def route_enterprise_agent(
    state: AgentState,
) -> Literal[
    "tools",
    "respond",
]:

    messages = state.get(
        "messages",
        [],
    )

    if not messages:
        return "respond"

    last_message = messages[-1]

    if getattr(
        last_message,
        "tool_calls",
        None,
    ):
        return "tools"

    return "respond"


def build_graph():

    builder = StateGraph(
        AgentState
    )

    builder.add_node(
        "classify",
        classify_intent,
    )

    builder.add_node(
        "enterprise_agent",
        enterprise_agent,
    )

    builder.add_node(
        "tools",
        tool_node,
    )

    builder.add_node(
        "general",
        handle_general_question,
    )

    builder.add_node(
        "respond",
        generate_final_response,
    )

    builder.add_edge(
        START,
        "classify",
    )

    builder.add_conditional_edges(
        "classify",
        route_by_intent,
    )

    builder.add_conditional_edges(
        "enterprise_agent",
        route_enterprise_agent,
    )

    builder.add_edge(
        "tools",
        "enterprise_agent",
    )

    builder.add_edge(
        "general",
        "respond",
    )

    builder.add_edge(
        "respond",
        END,
    )

    return builder.compile()


agent_graph = build_graph()