import asyncio
from typing import Literal

from pydantic import BaseModel

from app.llm.factory import (
    get_agent_model,
)


class TestClassification(BaseModel):
    intent: Literal[
        "enterprise",
        "general",
    ]


async def main():

    llm = get_agent_model()

    structured_llm = (
        llm.with_structured_output(
            TestClassification
        )
    )

    result = await structured_llm.ainvoke(
        """
        Classify this request:

        Why did deployment PAY-2026-0812 fail?

        enterprise:
        requires internal enterprise information

        general:
        does not require enterprise information
        """
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())