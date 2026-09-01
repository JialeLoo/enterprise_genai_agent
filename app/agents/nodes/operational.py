from app.agents.state import AgentState


def handle_operational_query(state: AgentState) -> dict:

    query = state["user_query"]

    mock_result = {
        "source": "deployment_system",
        "status": "failed",
        "deployment_id": "PAY-2026-0812",
        "reason": "database connection timeout",
    }

    return {
        "tool_results": [
            mock_result
        ],
        "draft_answer": (
            f"Operational data was retrieved for: {query}"
        ),
    }