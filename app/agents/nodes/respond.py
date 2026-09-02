from langchain_core.messages import AIMessage

from app.agents.state import AgentState


def generate_final_response(
    state: AgentState,
) -> dict:

    messages = state.get(
        "messages",
        [],
    )

    for message in reversed(messages):

        if (
            isinstance(message, AIMessage)
            and message.content
            and not message.tool_calls
        ):
            return {
                "final_answer":
                    str(message.content)
            }

    draft_answer = state.get(
        "draft_answer"
    )

    if draft_answer:
        return {
            "final_answer":
                draft_answer
        }

    return {
        "final_answer": (
            "I could not generate a response."
        )
    }