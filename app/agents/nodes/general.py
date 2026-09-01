from app.agents.state import AgentState


def handle_general_question(state: AgentState) -> dict:

    return {
        "draft_answer": (
            "This appears to be a general question "
            "that does not require enterprise data."
        )
    }