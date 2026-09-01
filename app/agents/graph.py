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

from app.agents.nodes.retrieve import (
    retrieve_knowledge,
)

from app.agents.nodes.general import (
    handle_general_question,
)

from app.agents.nodes.respond import (
    generate_final_response,
)

from app.agents.nodes.operational_agent import (
    operational_agent,
)

from app.tools import OPERATIONAL_TOOLS

from app.agents.nodes.knowledge_agent import (
    generate_knowledge_answer,
)


tool_node = ToolNode(
    OPERATIONAL_TOOLS
)


def route_by_intent(
    state: AgentState,
) -> Literal[
    "retrieve",
    "operational_agent",
    "general",
]:

    confidence = state.get(
        "classification_confidence",
        0.0,
    )

    if confidence < 0.65:
        return "general"

    intent = state["intent"]

    if intent == "knowledge_question":
        return "retrieve"

    if intent == "operational_query":
        return "operational_agent"

    return "general"


def route_operational_agent(
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
        "retrieve",
        retrieve_knowledge,
    )

    builder.add_node(
        "operational_agent",
        operational_agent,
    )

    builder.add_node(
        "knowledge_answer",
        generate_knowledge_answer,
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

    builder.add_edge(
        "retrieve",
        "knowledge_answer",
    )

    builder.add_edge(
        "knowledge_answer",
        END,
    )

    builder.add_edge(
        "general",
        "respond",
    )

    builder.add_conditional_edges(
        "operational_agent",
        route_operational_agent,
    )

    builder.add_edge(
        "tools",
        "operational_agent",
    )

    builder.add_edge(
        "respond",
        END,
    )

    return builder.compile()


agent_graph = build_graph()