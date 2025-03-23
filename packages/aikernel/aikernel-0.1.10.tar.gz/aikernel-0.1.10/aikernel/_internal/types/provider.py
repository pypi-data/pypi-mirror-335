from typing import Any, Literal, NotRequired, TypedDict


class LiteLLMTextMessagePart(TypedDict):
    type: Literal["text"]
    text: str


class LiteLLMMediaMessagePart(TypedDict):
    type: Literal["image_url"]
    image_url: str


class LiteLLMCacheControl(TypedDict):
    type: Literal["ephemeral"]


class LiteLLMMessage(TypedDict):
    role: Literal["system", "user", "assistant", "tool"]
    content: list[LiteLLMTextMessagePart | LiteLLMMediaMessagePart] | str
    tool_call_id: NotRequired[str]
    name: NotRequired[str]
    cache_control: NotRequired[LiteLLMCacheControl]


class LiteLLMToolFunction(TypedDict):
    name: str
    description: str
    parameters: dict[str, Any]


class LiteLLMTool(TypedDict):
    type: Literal["function"]
    function: LiteLLMToolFunction
