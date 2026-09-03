from langchain_core.messages import BaseMessage
from langchain_core.messages.base import (
    message_to_dict,
    messages_from_dict,
)


def serialize_messages(
    messages: list[BaseMessage],
) -> list[dict]:
    # LangChain's canonical representation retains tool calls, message IDs and
    # provider metadata. Keeping the full AI tool call is essential because a
    # later ToolMessage refers to it by ID when a conversation is restored.
    return [message_to_dict(message) for message in messages]


def deserialize_messages(
    data: list[dict],
) -> list[BaseMessage]:
    if not data:
        return []

    # Existing Redis conversations used a small legacy shape. Supporting it
    # lets deployments upgrade without first flushing all conversation keys.
    if "data" not in data[0]:
        data = [
            {
                "type": item["type"],
                "data": {
                    "content": item["content"],
                    **(
                        {"tool_call_id": item["tool_call_id"]}
                        if item["type"] == "tool"
                        else {}
                    ),
                },
            }
            for item in data
        ]

    return messages_from_dict(data)
