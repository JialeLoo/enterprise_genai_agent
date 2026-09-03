import asyncio
import json
import uuid
from pathlib import Path

from app.agents.graph import agent_graph

from evaluation.utils import (
    calculate_fact_score,
    calculate_tool_score,
    extract_tool_calls,
)

from app.observability.langfuse import (
    get_langfuse_handler,
)


CASES_PATH = (
    Path(__file__).parent
    / "agent_cases.json"
)


def load_cases() -> list[dict]:

    with open(
        CASES_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


async def evaluate_case(
    case: dict,
) -> dict:

    conversation_id = (
        f"eval-{uuid.uuid4()}"
    )

    langfuse_handler = (
        get_langfuse_handler()
    )

    result = await agent_graph.ainvoke(
        {
            "conversation_id":
                conversation_id,

            "user_query":
                case["input"],

            "messages":
                [],
        },
        config={
            "recursion_limit": 10,

            "callbacks": [
                langfuse_handler
            ],

            "run_name":
                "agent-evaluation",

            "metadata": {
                "evaluation_case":
                    case["name"],

                "evaluation":
                    True,
            },
        },
    )

    messages = result.get(
        "messages",
        [],
    )

    actual_tools = extract_tool_calls(
        messages
    )

    final_answer = result.get(
        "final_answer",
        "",
    )

    tool_score = (
        calculate_tool_score(
            case.get(
                "expected_tools",
                [],
            ),
            actual_tools,
        )
    )

    fact_score = (
        calculate_fact_score(
            case.get(
                "expected_facts",
                [],
            ),
            final_answer,
        )
    )

    overall_score = (
        tool_score + fact_score
    ) / 2

    return {
        "name":
            case["name"],

        "input":
            case["input"],

        "expected_tools":
            case.get(
                "expected_tools",
                [],
            ),

        "actual_tools":
            actual_tools,

        "tool_score":
            tool_score,

        "expected_facts":
            case.get(
                "expected_facts",
                [],
            ),

        "fact_score":
            fact_score,

        "overall_score":
            overall_score,

        "answer":
            final_answer,
    }


async def main():

    cases = load_cases()

    results = []

    for case in cases:

        print(
            f"\nRunning: "
            f"{case['name']}"
        )

        result = await evaluate_case(
            case
        )

        results.append(result)

        print(
            "Tools expected:",
            result["expected_tools"],
        )

        print(
            "Tools actual:",
            result["actual_tools"],
        )

        print(
            "Tool score:",
            f"{result['tool_score']:.2f}",
        )

        print(
            "Fact score:",
            f"{result['fact_score']:.2f}",
        )

        print(
            "Overall:",
            f"{result['overall_score']:.2f}",
        )

    average_tool_score = (
        sum(
            r["tool_score"]
            for r in results
        )
        / len(results)
    )

    average_fact_score = (
        sum(
            r["fact_score"]
            for r in results
        )
        / len(results)
    )

    average_overall_score = (
        sum(
            r["overall_score"]
            for r in results
        )
        / len(results)
    )

    print("\n======================")
    print("EVALUATION SUMMARY")
    print("======================")

    print(
        "Cases:",
        len(results),
    )

    print(
        "Average tool score:",
        f"{average_tool_score:.2%}",
    )

    print(
        "Average fact score:",
        f"{average_fact_score:.2%}",
    )

    print(
        "Average overall score:",
        f"{average_overall_score:.2%}",
    )


if __name__ == "__main__":
    asyncio.run(main())