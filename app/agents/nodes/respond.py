from app.agents.state import AgentState


def generate_final_response(state: AgentState) -> dict:

    intent = state.get("intent")

    if intent == "operational_query":

        tool_results = state.get(
            "tool_results",
            [],
        )

        if not tool_results:
            answer = (
                "I could not retrieve operational information."
            )

        else:
            result = tool_results[0]

            answer = (
                f"Deployment {result['deployment_id']} "
                f"is currently {result['status']}. "
                f"The reported reason is "
                f"{result['reason']}."
            )

    elif intent == "knowledge_question":

        context = state.get(
            "retrieved_context",
            [],
        )

        answer = "\n".join(context)

    else:

        answer = state.get(
            "draft_answer",
            "I could not generate a response.",
        )

    return {
        "final_answer": answer
    }