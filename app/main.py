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
from app.schemas import ChatRequest, ChatResponse
from app.security.rate_limit import enforce_rate_limit


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
    # 1. Identify the caller for rate limiting
    client_id = (
        request.client.host
        if request.client
        else "unknown"
    )

    # 2. Check Redis rate limit
    await enforce_rate_limit(client_id)

    # 3. Reuse conversation ID or create a new one
    conversation_id = (
        request_body.conversation_id
        or str(uuid.uuid4())
    )

    # 4. Load previous conversation from Redis
    stored_messages = await load_conversation(
        conversation_id
    )

    messages = deserialize_messages(
        stored_messages
    )

    # 5. Start LangGraph with restored history
    result = await agent_graph.ainvoke(
        {
            "conversation_id": conversation_id,
            "user_query": request_body.message,
            "messages": messages,
        },
        config={
            "recursion_limit": 10,
        },
    )

    # 6. Get updated graph messages
    result_messages = result.get(
        "messages",
        [],
    )

    # 7. Convert LangChain messages into JSON
    serialized_messages = serialize_messages(
        result_messages
    )

    # 8. Save updated conversation back to Redis
    await save_conversation(
        conversation_id,
        serialized_messages,
    )

    # 9. Return only the final answer to API caller
    return ChatResponse(
        conversation_id=conversation_id,
        answer=result["final_answer"],
    )