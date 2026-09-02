import asyncio

from langchain_core.messages import (
    HumanMessage,
)

from app.llm.factory import (
    get_agent_model,
)

from app.tools import ENTERPRISE_TOOLS


async def main():

    llm = get_agent_model()

    llm_with_tools = llm.bind_tools(
        ENTERPRISE_TOOLS
    )

    response = await llm_with_tools.ainvoke(
        [
            HumanMessage(
                content=(
                    "Why did deployment "
                    "PAY-2026-0812 fail?"
                )
            )
        ]
    )

    print(
        "CONTENT:",
        response.content,
    )

    print(
        "TOOL CALLS:",
        response.tool_calls,
    )


if __name__ == "__main__":
    asyncio.run(main())