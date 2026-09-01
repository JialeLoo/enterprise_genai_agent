import httpx

from app.config import get_settings


class OperationsClient:

    def __init__(self):
        settings = get_settings()

        self.base_url = (
            settings.operations_api_url.rstrip("/")
        )

        self.timeout = httpx.Timeout(
            timeout=5.0
        )

    async def get_deployment(
        self,
        deployment_id: str,
    ) -> dict:

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            response = await client.get(
                f"{self.base_url}/deployments/"
                f"{deployment_id}"
            )

            response.raise_for_status()

            return response.json()

    async def get_incidents(
        self,
        service: str,
    ) -> list[dict]:

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            response = await client.get(
                f"{self.base_url}/incidents",
                params={
                    "service": service
                },
            )

            response.raise_for_status()

            return response.json()

    async def get_logs(
        self,
        service: str,
    ) -> list[dict]:

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            response = await client.get(
                f"{self.base_url}/logs/{service}"
            )

            response.raise_for_status()

            return response.json()