import uuid

from fastapi import FastAPI, Request

from app.agents.graph import agent_graph
from app.config import get_settings
from app.memory.conversation_store import (
    load_conversation,
    save_conversation,
)
from app.memory.message_serializer import (
    deserialize_messages,
    serialize_messages,
)
from app.observability.langfuse import (
    get_langfuse_handler,
)
from app.schemas import (
    ChatRequest,
    ChatResponse,
)
from app.security.rate_limit import (
    enforce_rate_limit,
)

from app.agents.nodes.enterprise_agent import (
    ENTERPRISE_PROMPT_VERSION,
)


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "environment": settings.environment,
    }


@app.post(
    "/api/v1/chat",
    response_model=ChatResponse,
)
async def chat(
    request_body: ChatRequest,
    request: Request,
):
    # --------------------------------------------------
    # 1. Identify caller for basic rate limiting
    # --------------------------------------------------

    client_id = (
        request.client.host
        if request.client
        else "unknown"
    )

    await enforce_rate_limit(client_id)

    # --------------------------------------------------
    # 2. Resolve conversation ID
    # --------------------------------------------------

    conversation_id = (
        request_body.conversation_id
        or str(uuid.uuid4())
    )

    # --------------------------------------------------
    # 3. Load previous conversation from Redis
    # --------------------------------------------------

    stored_messages = await load_conversation(
        conversation_id
    )

    messages = deserialize_messages(
        stored_messages
    )

    # --------------------------------------------------
    # 4. Create Langfuse callback handler
    # --------------------------------------------------

    langfuse_handler = (
        get_langfuse_handler()
    )

    # --------------------------------------------------
    # 5. Run LangGraph
    # --------------------------------------------------

    result = await agent_graph.ainvoke(
        {
            "conversation_id":
                conversation_id,

            "user_query":
                request_body.message,

            "messages":
                messages,
        },
        config={
            "recursion_limit": 10,

            "callbacks": [
                langfuse_handler
            ],

            "run_name":
                "enterprise-genai-chat",

            "metadata": {
                "langfuse_session_id":
                    conversation_id,

                "environment":
                    settings.environment,

                "classifier_provider":
                    settings.classifier_provider,

                "classifier_model":
                    settings.classifier_model,

                "agent_provider":
                    settings.agent_provider,

                "agent_model":
                    settings.agent_model,

                "prompt_version":
                    ENTERPRISE_PROMPT_VERSION,
            },
        },
    )

    # --------------------------------------------------
    # 6. Persist updated conversation into Redis
    # --------------------------------------------------

    result_messages = result.get(
        "messages",
        [],
    )

    serialized_messages = (
        serialize_messages(
            result_messages
        )
    )

    await save_conversation(
        conversation_id,
        serialized_messages,
    )

    # --------------------------------------------------
    # 7. Return API response
    # --------------------------------------------------

    return ChatResponse(
        conversation_id=conversation_id,
        answer=result["final_answer"],
    )


@app.post("/api/v1/debug/chat")
async def debug_chat(
    request_body: ChatRequest,
):
    conversation_id = (
        request_body.conversation_id
        or str(uuid.uuid4())
    )

    stored_messages = await load_conversation(
        conversation_id
    )

    messages = deserialize_messages(
        stored_messages
    )

    langfuse_handler = (
        get_langfuse_handler()
    )

    result = await agent_graph.ainvoke(
        {
            "conversation_id":
                conversation_id,

            "user_query":
                request_body.message,

            "messages":
                messages,
        },
        config={
            "recursion_limit": 10,

            "callbacks": [
                langfuse_handler
            ],

            "run_name":
                "enterprise-genai-debug",

            "metadata": {
                "langfuse_session_id":
                    conversation_id,

                "environment":
                    settings.environment,

                "classifier_provider":
                    settings.classifier_provider,

                "classifier_model":
                    settings.classifier_model,

                "agent_provider":
                    settings.agent_provider,

                "agent_model":
                    settings.agent_model,

                "prompt_version":
                    "enterprise-agent-v1",
            },
        },
    )

    result_messages = result.get(
        "messages",
        [],
    )

    serialized_messages = (
        serialize_messages(
            result_messages
        )
    )

    await save_conversation(
        conversation_id,
        serialized_messages,
    )

    return result