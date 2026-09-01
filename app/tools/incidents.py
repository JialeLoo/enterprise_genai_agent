from langchain_core.tools import tool

from app.clients.operations_client import (
    OperationsClient,
)


@tool
async def get_incidents(
    service: str,
) -> list[dict]:
    """
    Retrieve incidents associated with a service.

    Use this when the user asks about outages,
    incidents, production problems, or service
    disruptions.
    """

    client = OperationsClient()

    return await client.get_incidents(
        service
    )