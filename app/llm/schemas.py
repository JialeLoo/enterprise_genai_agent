from typing import Literal

from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    intent: Literal[
        "enterprise_query",
        "general_question",
    ]

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    reasoning: str