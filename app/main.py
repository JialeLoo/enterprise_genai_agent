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


async def run_agent_chat(
    request_body: ChatRequest,
    *,
    run_name: str,
) -> tuple[str, dict]:
    """Run and persist one conversation turn for either chat endpoint."""
    conversation_id = (
        request_body.conversation_id
        or str(uuid.uuid4())
    )

    stored_messages = await load_conversation(
        conversation_id
    )
    messages = deserialize_messages(stored_messages)

    # A fresh callback per graph invocation keeps traces scoped to one request.
    langfuse_handler = get_langfuse_handler()
    result = await agent_graph.ainvoke(
        {
            "conversation_id": conversation_id,
            "user_query": request_body.message,
            "messages": messages,
        },
        config={
            # Bounds the model -> tools -> model loop if a model repeatedly
            # requests tools without producing a final answer.
            "recursion_limit": 10,
            "callbacks": [langfuse_handler],
            "run_name": run_name,
            "metadata": {
                "langfuse_session_id": conversation_id,
                "environment": settings.environment,
                "classifier_provider": settings.classifier_provider,
                "classifier_model": settings.classifier_model,
                "agent_provider": settings.agent_provider,
                "agent_model": settings.agent_model,
                "prompt_version": ENTERPRISE_PROMPT_VERSION,
            },
        },
    )

    # Persist the graph's merged state, including tool-call messages needed to
    # give the next request a valid conversational transcript.
    await save_conversation(
        conversation_id,
        serialize_messages(result.get("messages", [])),
    )
    return conversation_id, result


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
    # IP-based limiting is intentionally basic for this POC. Production should
    # key this by authenticated user/tenant and handle trusted proxy headers.
    client_id = (
        request.client.host
        if request.client
        else "unknown"
    )

    await enforce_rate_limit(client_id)
    conversation_id, result = await run_agent_chat(
        request_body,
        run_name="enterprise-genai-chat",
    )

    return ChatResponse(
        conversation_id=conversation_id,
        answer=result["final_answer"],
    )


@app.post("/api/v1/debug/chat")
async def debug_chat(
    request_body: ChatRequest,
):
    _, result = await run_agent_chat(
        request_body,
        run_name="enterprise-genai-debug",
    )

    return result
