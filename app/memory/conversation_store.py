import json

from app.cache.redis_client import (
    get_redis_client,
)


CONVERSATION_TTL_SECONDS = 3600


async def load_conversation(
    conversation_id: str,
) -> list[dict]:

    redis = get_redis_client()

    key = (
        f"conversation:"
        f"{conversation_id}"
    )

    value = await redis.get(key)

    if not value:
        return []

    return json.loads(value)


async def save_conversation(
    conversation_id: str,
    messages: list[dict],
) -> None:

    redis = get_redis_client()

    key = (
        f"conversation:"
        f"{conversation_id}"
    )

    await redis.set(
        key,
        json.dumps(messages),
        ex=CONVERSATION_TTL_SECONDS,
    )