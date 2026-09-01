import uuid

from fastapi import FastAPI

from app.agents.graph import agent_graph
from app.config import get_settings
from app.schemas import ChatRequest, ChatResponse


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
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
async def chat(request: ChatRequest):
    conversation_id = (
        request.conversation_id
        or str(uuid.uuid4())
    )

    result = await agent_graph.ainvoke(
        {
            "conversation_id": conversation_id,
            "user_query": request.message,
        }
    )

    return ChatResponse(
        conversation_id=conversation_id,
        answer=result["final_answer"],
    )


@app.post("/api/v1/debug/chat")
async def debug_chat(request: ChatRequest):
    conversation_id = (
        request.conversation_id
        or str(uuid.uuid4())
    )

    result = await agent_graph.ainvoke(
        {
            "conversation_id": conversation_id,
            "user_query": request.message,
        }
    )

    return result