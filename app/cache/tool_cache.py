import json

from app.cache.redis_client import (
    get_redis_client,
)


async def get_cached_json(
    key: str,
) -> dict | list | None:

    redis = get_redis_client()

    value = await redis.get(key)

    if not value:
        return None

    return json.loads(value)


async def set_cached_json(
    key: str,
    value: dict | list,
    ttl_seconds: int,
) -> None:

    redis = get_redis_client()

    await redis.set(
        key,
        json.dumps(value),
        ex=ttl_seconds,
    )