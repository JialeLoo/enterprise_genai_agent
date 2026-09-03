from langchain_core.messages import AIMessage


def extract_tool_calls(
    messages,
) -> list[str]:
    """
    Extract every tool name requested by
    AI messages during the graph execution.
    """

    tool_names: list[str] = []

    for message in messages:

        if not isinstance(
            message,
            AIMessage,
        ):
            continue

        for tool_call in (
            message.tool_calls or []
        ):
            tool_name = tool_call.get(
                "name"
            )

            if tool_name:
                tool_names.append(
                    tool_name
                )

    return tool_names


def calculate_tool_score(
    expected_tools: list[str],
    actual_tools: list[str],
) -> float:
    """
    Score whether all required tools were used.

    Extra tool calls do not immediately make
    the case fail.
    """

    if not expected_tools:
        return 1.0

    expected = set(expected_tools)
    actual = set(actual_tools)

    matched = expected.intersection(
        actual
    )

    return (
        len(matched)
        / len(expected)
    )


def calculate_fact_score(
    expected_facts: list[str],
    answer: str,
) -> float:
    """
    Simple deterministic grounding check.

    A fact counts as present when its expected
    text occurs in the final answer.
    """

    if not expected_facts:
        return 1.0

    normalized_answer = (
        answer.lower()
    )

    matched = 0

    for fact in expected_facts:

        if fact.lower() in normalized_answer:
            matched += 1

    return (
        matched
        / len(expected_facts)
    )