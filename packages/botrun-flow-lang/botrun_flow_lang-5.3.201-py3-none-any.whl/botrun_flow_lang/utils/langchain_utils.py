from copy import deepcopy
from typing import Dict, List, Any
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
    AIMessageChunk,
    message_to_dict,
)
import json


def litellm_msgs_to_langchain_msgs(
    msgs: List[Dict], enable_prompt_caching: bool = False
) -> List[BaseMessage]:
    """
    Convert LiteLLM style messages to Langchain messages.

    Args:
        msgs: List of dictionaries with 'role' and 'content' keys
        enable_prompt_caching: Whether to enable prompt caching, anthropic only
    Returns:
        List of Langchain message objects
    """
    converted_msgs = []
    for msg in msgs:
        role = msg["role"]
        content = msg["content"]

        if role == "system":
            if enable_prompt_caching:
                converted_msgs.append(
                    SystemMessage(
                        content=[
                            {
                                "text": content,
                                "type": "text",
                                "cache_control": {"type": "ephemeral"},
                            }
                        ]
                    )
                )
            else:
                converted_msgs.append(SystemMessage(content=content))
        elif role == "user":
            if enable_prompt_caching and isinstance(content, str):
                converted_msgs.append(
                    HumanMessage(
                        content=[
                            {
                                "text": content,
                                "type": "text",
                                "cache_control": {"type": "ephemeral"},
                            }
                        ]
                    )
                )
            elif enable_prompt_caching and isinstance(content, list):
                for item in content:
                    converted_msgs.append(
                        HumanMessage(
                            content=[
                                {
                                    "text": item.get("text", ""),
                                    "type": "text",
                                    "cache_control": {"type": "ephemeral"},
                                }
                            ]
                        )
                    )
            elif content != "":
                converted_msgs.append(HumanMessage(content=content))
        elif role == "assistant":
            if enable_prompt_caching:
                converted_msgs.append(
                    AIMessage(
                        content=[
                            {
                                "text": content,
                                "type": "text",
                                "cache_control": {"type": "ephemeral"},
                            }
                        ]
                    )
                )
            elif content != "":
                converted_msgs.append(AIMessage(content=content))
        else:
            raise ValueError(f"Unsupported role: {role}")

    return converted_msgs


def langgraph_msgs_to_json(messages: List) -> Dict:
    new_messages = []
    for message in messages:
        if isinstance(message, BaseMessage):
            msg_dict = message_to_dict(message)
            new_messages.append(msg_dict)
        elif isinstance(message, list):
            inner_messages = []
            for inner_message in message:
                if isinstance(inner_message, BaseMessage):
                    inner_messages.append(message_to_dict(inner_message))
                else:
                    inner_messages.append(inner_message)
            new_messages.append(inner_messages)
        else:
            new_messages.append(message)
    return new_messages


def convert_nested_structure(obj: Any) -> Any:
    """
    Recursively convert BaseMessage objects in nested dictionaries and lists.

    Args:
        obj: Any object that might contain BaseMessage objects

    Returns:
        A new object with all BaseMessage objects converted to dictionaries
    """
    if isinstance(obj, BaseMessage):
        return message_to_dict(obj)
    elif isinstance(obj, dict):
        return {key: convert_nested_structure(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_nested_structure(item) for item in obj]
    else:
        return obj


def langgraph_event_to_json(event: Dict) -> str:
    """
    Convert a LangGraph event to JSON string, handling all nested BaseMessage objects.

    Args:
        event: Dictionary containing LangGraph event data

    Returns:
        JSON string representation of the event
    """
    new_event = deepcopy(event)
    new_event = convert_nested_structure(new_event)
    return json.dumps(new_event, ensure_ascii=False)
