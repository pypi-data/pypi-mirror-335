import json
from typing import Literal

from anthropic.types import Message as AnthropicMessage
from anthropic.types.text_block import TextBlock
from anthropic.types.tool_use_block import ToolUseBlock
from openai.types.chat import ChatCompletion

from moxn import base_models as tp
from moxn.base_models.telemetry import LLMResponse, ToolCall

StopReasonType = Literal[
    "stop", "length", "tool_calls", "content_filter", "function_call"
]


def unpack_llm_response_content(
    llm_response: ChatCompletion | AnthropicMessage, provider: tp.Provider
) -> LLMResponse:
    """
    Unpacks the content from an LLM response based on the provider.

    Args:
        llm_response: The response from the LLM (OpenAI or Anthropic)
        provider: The provider of the LLM (OpenAI or Anthropic)

    Returns:
        LLMResponse: A standardized response object with content, tool calls, etc.

    Raises:
        ValueError: If the provider is not supported or content type is unexpected
    """
    message_content = None
    tool_calls = []
    metadata = {}

    if provider == tp.Provider.OPENAI:
        if not isinstance(llm_response, ChatCompletion):
            raise ValueError(f"Unsupported OpenAI response type: {type(llm_response)}")
        choice = llm_response.choices[0]
        message = choice.message

        # Handle content which may be None for tool-only responses
        message_content = message.content if hasattr(message, "content") else None

        # Process tool calls if they exist
        if hasattr(message, "tool_calls") and message.tool_calls:
            tool_calls = [
                ToolCall(
                    name=call.function.name,
                    arguments=(
                        json.loads(call.function.arguments)
                        if isinstance(call.function.arguments, str)
                        else call.function.arguments
                    ),
                )
                for call in message.tool_calls
            ]

        stop_reason = choice.finish_reason
        metadata = {
            "model": llm_response.model,
            "usage": (
                llm_response.usage.model_dump()  # type: ignore
                if hasattr(llm_response.usage, "model_dump")
                else llm_response.usage
            ),
        }

    elif provider == tp.Provider.ANTHROPIC:
        if not isinstance(llm_response, AnthropicMessage):
            raise ValueError(
                f"Unsupported Anthropic response type: {type(llm_response)}"
            )
        # Handle Anthropic's content structure which is a list of blocks
        if hasattr(llm_response, "content") and llm_response.content:
            for content_block in llm_response.content[0]:
                if isinstance(content_block, TextBlock):
                    message_content = content_block.text
                elif isinstance(content_block, ToolUseBlock):
                    # For tool use blocks, we might want to capture some representation
                    # of the tool use in message_content
                    if message_content is None:
                        message_content = f"Tool use: {content_block.name}"

                    # Add to tool calls
                    tool_calls.append(
                        ToolCall(
                            name=content_block.name,
                            arguments=content_block.input,  # type: ignore
                        )
                    )
                else:
                    raise ValueError(
                        f"Unsupported Anthropic content block type: {type(content_block)}"
                    )

        # Process tool calls from the dedicated attribute if it exists
        if hasattr(llm_response, "tool_calls") and llm_response.tool_calls:  # type: ignore
            # Only add tool calls that weren't already processed from content blocks
            existing_tool_names = {call.name for call in tool_calls}
            for call in llm_response.tool_calls:  # type: ignore
                if call.name not in existing_tool_names:
                    tool_calls.append(
                        ToolCall(name=call.name, arguments=call.arguments)
                    )

        # Map Anthropic stop reasons to OpenAI-compatible format
        stop_reason_mapping: dict[str, StopReasonType] = {
            "end_turn": "stop",
            "max_tokens": "length",
            "stop_sequence": "stop",
            "tool_use": "tool_calls",
        }

        # Default value must also be one of the allowed literals
        default_stop_reason: StopReasonType = "stop"

        # Convert Anthropic stop reason to compatible format
        raw_stop_reason = llm_response.stop_reason
        stop_reason: StopReasonType | None = (  # type: ignore
            stop_reason_mapping.get(raw_stop_reason, default_stop_reason)
            if raw_stop_reason
            else None
        )

        metadata = {
            "model": llm_response.model,
            "usage": (
                llm_response.usage.model_dump()
                if hasattr(llm_response.usage, "model_dump")
                else llm_response.usage
            ),
        }
    else:
        raise ValueError(
            f"Unsupported provider or response type: {provider}, {type(llm_response)}"
        )

    return LLMResponse(
        content=message_content,
        tool_calls=tool_calls,
        stop_reason=stop_reason,
        metadata=metadata,
    )
