from langchain_core.tools import tool

from app.clients.operations_client import (
    OperationsClient,
)


@tool
async def get_service_logs(
    service: str,
) -> list[dict]:
    """
    Retrieve recent application logs for a service.

    Use this when the user asks to inspect logs,
    errors, exceptions, warnings, or technical
    evidence about a service problem.
    """

    client = OperationsClient()

    return await client.get_logs(
        service
    )