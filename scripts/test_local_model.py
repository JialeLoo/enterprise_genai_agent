import asyncio

from app.llm.factory import (
    get_agent_model,
)


async def main():

    llm = get_agent_model()

    response = await llm.ainvoke(
        "Explain what Redis is "
        "in one sentence."
    )

    print(response.content)


if __name__ == "__main__":
    asyncio.run(main())