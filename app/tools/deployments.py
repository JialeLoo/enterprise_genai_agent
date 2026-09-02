from langchain_core.tools import tool

from app.cache.tool_cache import (
    get_cached_json,
    set_cached_json,
)
from app.clients.operations_client import (
    OperationsClient,
)


@tool
async def get_deployment(
    deployment_id: str,
) -> dict:
    """
    Retrieve information about a deployment.
    """

    normalized_id = (
        deployment_id.upper()
    )

    cache_key = (
        f"deployment:"
        f"{normalized_id}"
    )

    cached = await get_cached_json(
        cache_key
    )

    if cached is not None:
        return cached

    client = OperationsClient()

    result = await client.get_deployment(
        normalized_id
    )

    await set_cached_json(
        key=cache_key,
        value=result,
        ttl_seconds=300,
    )

    return result