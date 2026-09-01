from langchain_core.tools import tool

from app.clients.operations_client import (
    OperationsClient,
)


@tool
async def get_deployment(
    deployment_id: str,
) -> dict:
    """
    Retrieve information about a deployment.

    Use this when the user asks about a specific
    deployment, including its status, version,
    timestamp, or failure reason.
    """

    client = OperationsClient()

    return await client.get_deployment(
        deployment_id
    )