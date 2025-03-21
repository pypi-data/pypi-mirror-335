from enum import Enum
from typing import Literal, overload

from anthropic.types import ImageBlockParam, MessageParam, TextBlockParam
from anthropic.types.image_block_param import Source
from openai.types.chat import (
    ChatCompletionContentPartImageParam,
    ChatCompletionMessageParam,
)
from openai.types.chat.chat_completion_content_part_image_param import ImageURL
from openai.types.chat.chat_completion_content_part_text_param import (
    ChatCompletionContentPartTextParam,
)
from pydantic import BaseModel


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    SCHEMA = "schema"


class Provider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class Author(Enum):
    HUMAN = "human"
    MACHINE = "machine"


class BaseContent(BaseModel):
    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.ANTHROPIC]
    ) -> TextBlockParam | ImageBlockParam: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.OPENAI]
    ) -> ChatCompletionContentPartTextParam | ChatCompletionContentPartImageParam: ...

    def to_provider_content_block(self, provider: Provider):
        raise NotImplementedError


class TextContent(BaseContent):
    text: str

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.ANTHROPIC]
    ) -> TextBlockParam: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.OPENAI]
    ) -> ChatCompletionContentPartTextParam: ...

    def to_provider_content_block(
        self, provider: Provider
    ) -> TextBlockParam | ChatCompletionContentPartTextParam:
        if provider == Provider.ANTHROPIC:
            return TextBlockParam(type="text", text=self.text)
        elif provider == Provider.OPENAI:
            return ChatCompletionContentPartTextParam(type="text", text=self.text)


class ImageContentUrl(BaseContent):
    image_url: str

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.ANTHROPIC]
    ) -> ImageBlockParam: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.OPENAI]
    ) -> ChatCompletionContentPartImageParam: ...

    def to_provider_content_block(
        self, provider: Provider
    ) -> ChatCompletionContentPartImageParam | ImageBlockParam:
        if provider == Provider.ANTHROPIC:
            # TODO: Anthropic now supports image URLs so we need to update this
            return ImageBlockParam(
                source={"type": "base64", "media_type": "image/png", "data": ""},
                type="image",
            )
        elif provider == Provider.OPENAI:
            return ChatCompletionContentPartImageParam(
                image_url=ImageURL(url=self.image_url, detail="auto"),
                type="image_url",
            )


class ImageContentBase64(BaseContent):
    type: Literal["image_base64"]
    media_type: Literal["image/png", "image/jpeg"]
    data: str

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.ANTHROPIC]
    ) -> ImageBlockParam: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.OPENAI]
    ) -> ChatCompletionContentPartImageParam: ...

    def to_provider_content_block(
        self, provider: Provider
    ) -> ChatCompletionContentPartImageParam | ImageBlockParam:
        if provider == Provider.ANTHROPIC:
            return ImageBlockParam(
                source=Source(
                    data=self.data, media_type=self.media_type, type="base64"
                ),
                type="image",
            )
        elif provider == Provider.OPENAI:
            return ChatCompletionContentPartImageParam(
                image_url=ImageURL(
                    url=f"data:{self.media_type};base64,{self.data}", detail="auto"
                ),
                type="image_url",
            )


class ProviderMessagesParam(BaseModel):
    """Base class for provider-specific message parameters"""

    pass


class OpenAIMessagesParam(ProviderMessagesParam):
    messages: list[ChatCompletionMessageParam]


class AnthropicMessagesParam(ProviderMessagesParam):
    system: str | list[TextBlockParam] | None = None
    messages: list[MessageParam]
