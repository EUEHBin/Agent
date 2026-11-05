from collections.abc import AsyncGenerator, Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import cast

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam


class MessageRole(StrEnum):
    """消息角色"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class AIMessage:
    """AI 消息"""

    role: MessageRole
    content: str


@dataclass
class AIChatConfig:
    """AI 聊天配置"""

    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o"


class AIChat:
    """AI 聊天类，封装 OpenAI 兼容接口的流式对话。"""

    def __init__(self, config: AIChatConfig):
        self._config = config
        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
        )

    async def chat_stream(
        self, messages: Iterable[AIMessage]
    ) -> AsyncGenerator[str, None]:
        """
        流式对话，传入历史消息记录，流式返回 AI 回复。

        Args:
            messages: 消息数组，格式为：
                      [AIMessage(role=MessageRole.USER, content="你好"), ...]

        Yields:
            AI 回复的文本片段。
        """
        payload = cast(
            list[ChatCompletionMessageParam],
            [{"role": msg.role.value, "content": msg.content} for msg in messages],
        )

        response = await self._client.chat.completions.create(
            model=self._config.model,
            messages=payload,
            stream=True,
        )

        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
