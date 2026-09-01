from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="Mock Enterprise Operations API",
    version="1.0.0",
)


DEPLOYMENTS = {
    "PAY-2026-0812": {
        "deployment_id": "PAY-2026-0812",
        "service": "payment-service",
        "version": "2.14.7",
        "previous_version": "2.14.6",
        "status": "failed",
        "reason": "database connection timeout",
        "timestamp": "2026-08-12T13:42:00Z",
    },

    "AUTH-2026-0901": {
        "deployment_id": "AUTH-2026-0901",
        "service": "auth-service",
        "version": "5.8.1",
        "previous_version": "5.8.0",
        "status": "successful",
        "reason": None,
        "timestamp": "2026-09-01T03:20:00Z",
    },
}


INCIDENTS = [
    {
        "incident_id": "INC-1042",
        "service": "payment-service",
        "severity": "SEV2",
        "status": "investigating",
        "description": (
            "Elevated HTTP 500 errors following deployment "
            "PAY-2026-0812."
        ),
    },
    {
        "incident_id": "INC-1043",
        "service": "customer-profile-service",
        "severity": "SEV3",
        "status": "resolved",
        "description": "Slow database queries.",
    },
]


LOGS = {
    "payment-service": [
        {
            "timestamp": "2026-08-12T13:42:13Z",
            "level": "ERROR",
            "message": "Database connection pool exhausted",
        },
        {
            "timestamp": "2026-08-12T13:42:14Z",
            "level": "ERROR",
            "message": "Database connection timeout",
        },
        {
            "timestamp": "2026-08-12T13:42:16Z",
            "level": "WARN",
            "message": "Circuit breaker failure threshold exceeded",
        },
    ]
}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/deployments/{deployment_id}")
async def get_deployment(
    deployment_id: str,
):
    deployment = DEPLOYMENTS.get(
        deployment_id.upper()
    )

    if not deployment:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found",
        )

    return deployment


@app.get("/incidents")
async def get_incidents(
    service: str | None = None,
):
    if not service:
        return INCIDENTS

    return [
        incident
        for incident in INCIDENTS
        if incident["service"] == service
    ]


@app.get("/logs/{service}")
async def get_logs(
    service: str,
):
    return LOGS.get(service, [])