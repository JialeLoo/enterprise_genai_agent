from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ToolMessage,
)


def serialize_messages(
    messages: list[BaseMessage],
) -> list[dict]:

    result = []

    for message in messages:

        if isinstance(
            message,
            HumanMessage,
        ):
            result.append(
                {
                    "type": "human",
                    "content":
                        message.content,
                }
            )

        elif isinstance(
            message,
            AIMessage,
        ):
            result.append(
                {
                    "type": "ai",
                    "content":
                        message.content,
                }
            )

        elif isinstance(
            message,
            ToolMessage,
        ):
            result.append(
                {
                    "type": "tool",
                    "content":
                        message.content,
                    "tool_call_id":
                        message.tool_call_id,
                }
            )

    return result

def deserialize_messages(
    data: list[dict],
) -> list[BaseMessage]:

    messages = []

    for item in data:

        message_type = item["type"]

        if message_type == "human":
            messages.append(
                HumanMessage(
                    content=item["content"]
                )
            )

        elif message_type == "ai":
            messages.append(
                AIMessage(
                    content=item["content"]
                )
            )

        elif message_type == "tool":
            messages.append(
                ToolMessage(
                    content=item["content"],
                    tool_call_id=item[
                        "tool_call_id"
                    ],
                )
            )

    return messages