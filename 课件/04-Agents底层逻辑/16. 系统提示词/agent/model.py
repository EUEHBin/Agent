from collections.abc import Iterator
from dataclasses import dataclass
from typing import cast
from agent.message import Message
from agent.config import openai_settings
from openai import OpenAI


@dataclass
class Chunk:
    type: str = ""
    content: str = ""


@dataclass
class Model:
    model_name: str = openai_settings.model
    _client: OpenAI = OpenAI()

    def invoke(self, messages: list[Message]):
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=cast(
                list, [{"role": m.role, "content": m.content} for m in messages]
            ),
        )
        return response

    def invoke_stream(self, messages: list[Message]) -> Iterator[Chunk]:
        stream = self._client.chat.completions.create(
            model=self.model_name,
            messages=cast(
                list, [{"role": m.role, "content": m.content} for m in messages]
            ),
            stream=True,
        )
        is_on_reasoning = False
        full_reasoning_content = ""  # 完整的思维链
        full_content = ""  # 完整的内容
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            content = delta.content
            reasoning_content = getattr(delta, "reasoning_content", None)
            if not reasoning_content:
                reasoning_content = getattr(delta, "reasoning", None)

            if reasoning_content:
                full_reasoning_content += reasoning_content
                if not is_on_reasoning:
                    is_on_reasoning = True
                    yield Chunk(type="reasoning_start")
                yield Chunk(type="reasoning", content=reasoning_content)
            if content:
                full_content += content
                if is_on_reasoning:
                    is_on_reasoning = False
                    yield Chunk(type="reasoning_end", content=full_reasoning_content)
                    yield Chunk(type="content_start")
                yield Chunk(type="content", content=content)

        yield Chunk(type="content_end", content=full_content)
