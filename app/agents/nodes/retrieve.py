from app.agents.state import AgentState


MOCK_DOCUMENTS = {
    "rollback": (
        "Deployment rollback procedure: "
        "If a production deployment causes elevated error rates, "
        "operators should validate service health and rollback to "
        "the previously stable version."
    ),
    "access": (
        "Production access policy: "
        "Production access requires approved authorization."
    ),
}


def retrieve_knowledge(state: AgentState) -> dict:
    query = state["user_query"].lower()

    retrieved_context = []

    if "rollback" in query or "deployment" in query:
        retrieved_context.append(
            MOCK_DOCUMENTS["rollback"]
        )

    if "access" in query:
        retrieved_context.append(
            MOCK_DOCUMENTS["access"]
        )

    if not retrieved_context:
        retrieved_context.append(
            "No relevant internal documentation was found."
        )

    return {
        "retrieved_context": retrieved_context,
        "draft_answer": (
            "I retrieved internal documentation "
            "relevant to the request."
        ),
    }