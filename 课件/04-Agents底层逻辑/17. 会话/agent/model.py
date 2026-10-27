from collections.abc import Iterator
from dataclasses import dataclass
from typing import cast

from agent.config import openai_settings
from agent.session import Session
from openai import OpenAI


@dataclass
class Chunk:
    type: str = ""
    content: str = ""


@dataclass
class Model:
    model_name: str = openai_settings.model
    _client: OpenAI = OpenAI()

    def invoke(self, messages: list[dict] | Session):
        session = None
        if isinstance(messages, Session):
            session = messages
            messages = session.messages

        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=cast(list, messages),
        )

        if session:
            content = response.choices[0].message.content or ""
            session.add_message(response.choices[0].message.to_dict())

        return response

    def invoke_stream(self, messages: list[dict] | Session) -> Iterator[Chunk]:
        session = None
        if isinstance(messages, Session):
            session = messages
            messages = session.messages

        stream = self._client.chat.completions.create(
            model=self.model_name,
            messages=cast(list, messages),
            stream=True,
        )
        is_on_reasoning = False
        full_reasoning_content = ""
        full_content = ""
        reasoning_field = ""
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            content = delta.content
            reasoning_field_temp = "reasoning_content"
            reasoning_content = getattr(delta, reasoning_field_temp, None)
            if not reasoning_content:
                reasoning_field_temp = "reasoning"
                reasoning_content = getattr(delta, reasoning_field_temp, None)
            if reasoning_content:
                reasoning_field = reasoning_field_temp

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

        if session:
            msg = {"role": "assistant", "content": full_content}
            if reasoning_field:
                msg[reasoning_field] = full_reasoning_content
            session.add_message(msg)
