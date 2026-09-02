from fastapi import HTTPException

from app.cache.redis_client import (
    get_redis_client,
)


RATE_LIMIT = 20
WINDOW_SECONDS = 60


async def enforce_rate_limit(
    client_id: str,
) -> None:

    redis = get_redis_client()

    key = (
        f"rate_limit:"
        f"{client_id}"
    )

    count = await redis.incr(key)

    if count == 1:
        await redis.expire(
            key,
            WINDOW_SECONDS,
        )

    if count > RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=(
                "Rate limit exceeded. "
                "Please try again later."
            ),
        )