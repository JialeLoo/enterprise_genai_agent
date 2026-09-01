from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.agents.nodes.classify import classify_intent
from app.agents.nodes.general import handle_general_question
from app.agents.nodes.operational import handle_operational_query
from app.agents.nodes.respond import generate_final_response
from app.agents.nodes.retrieve import retrieve_knowledge
from app.agents.state import AgentState


def route_by_intent(
    state: AgentState,
) -> Literal[
    "retrieve",
    "operational",
    "general",
]:

    intent = state["intent"]

    if intent == "knowledge_question":
        return "retrieve"

    if intent == "operational_query":
        return "operational"

    return "general"


def build_graph():

    builder = StateGraph(AgentState)

    builder.add_node(
        "classify",
        classify_intent,
    )

    builder.add_node(
        "retrieve",
        retrieve_knowledge,
    )

    builder.add_node(
        "operational",
        handle_operational_query,
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
        "respond",
    )

    builder.add_edge(
        "operational",
        "respond",
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