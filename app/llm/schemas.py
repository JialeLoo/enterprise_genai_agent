from typing import Literal

from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    intent: Literal[
        "knowledge_question",
        "operational_query",
        "general_question",
    ]

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the classification.",
    )

    reasoning: str = Field(
        description=(
            "Short explanation of why the query belongs "
            "to this intent."
        )
    )