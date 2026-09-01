from langchain_core.messages import AIMessage

from app.agents.state import AgentState


def generate_final_response(
    state: AgentState,
) -> dict:

    intent = state.get(
        "intent"
    )

    if intent == "operational_query":

        messages = state.get(
            "messages",
            [],
        )

        for message in reversed(messages):

            if (
                isinstance(
                    message,
                    AIMessage,
                )
                and message.content
                and not message.tool_calls
            ):

                return {
                    "final_answer":
                        str(message.content)
                }

        return {
            "final_answer": (
                "I could not generate an "
                "operational response."
            )
        }

    if intent == "knowledge_question":

        context = state.get(
            "retrieved_context",
            [],
        )

        return {
            "final_answer":
                "\n".join(context)
        }

    return {
        "final_answer":
            state.get(
                "draft_answer",
                "I could not generate a response.",
            )
    }