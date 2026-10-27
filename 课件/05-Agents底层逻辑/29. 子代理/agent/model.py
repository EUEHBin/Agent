from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
import json
from typing import Any, cast
from agent.events import EventEmitter, Event
from agent.config import openai_settings
from agent.session import Session
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk


def _get_reasoning_field_name(res_or_chunk):
    "为了兼容性，获取推理字段的名称"
    for attr_name in ["reasoning_content", "reasoning"]:
        if hasattr(res_or_chunk, attr_name):
            return attr_name
    return ""


@dataclass
class InvokeResult:
    message: dict
    raw: Any

    def print_raw(self):
        if isinstance(self.raw, ChatCompletion):
            print(self.raw.to_json(indent=2))
        else:
            data = [c.model_dump() for c in self.raw]
            print(json.dumps(data, ensure_ascii=False, indent=2))


class Builder(ABC):

    def __init__(self, emitter: EventEmitter):
        self.emitter = emitter
        self.value = None
        self.compoleted = False

    @abstractmethod
    def _key_names(self, delta) -> list[str]:
        "获取关键名称"
        pass

    def emit(self, chunk: ChatCompletionChunk):
        if self.compoleted:
            return
        if not chunk.choices:
            return
        delta = chunk.choices[0].delta
        field_name, start_event_name, event_name, end_event_name = self._key_names(
            delta
        )
        value = getattr(delta, field_name, None)
        if value:
            if not self.value:
                self.value = {field_name: value}
                self.emitter.emit(start_event_name)
            else:
                self.append_value(value, field_name)
            self.emitter.emit(event_name, chunk_value=value, chunk=chunk)
        if self.is_end(chunk):
            if self.value:
                self.emitter.emit(end_event_name, value=self.value, chunk=chunk)
                self.compoleted = True

    def append_value(self, value, field_name: str):
        self.value[field_name] += value  # type: ignore

    def is_end(self, chunk: ChatCompletionChunk):
        return bool(chunk.choices[0].finish_reason)


class ContentBuilder(Builder):
    def _key_names(self, delta):
        return ["content", Event.CONTENT_START, Event.CONTENT, Event.CONTENT_END]


class ReasoningBuilder(Builder):
    def _key_names(self, delta):
        return [
            _get_reasoning_field_name(delta),
            Event.REASONING_START,
            Event.REASONING,
            Event.REASONING_END,
        ]

    def is_end(self, chunk: ChatCompletionChunk):
        delta = chunk.choices[0].delta
        return bool(delta.content) or bool(delta.tool_calls) or super().is_end(chunk)


class ToolCallsBuilder(Builder):
    def _key_names(self, delta):
        return [
            "tool_calls",
            Event.TOOL_CALL_START,
            Event.TOOL_CALL,
            Event.TOOL_CALL_END,
        ]

    def emit(self, chunk: ChatCompletionChunk):
        super().emit(chunk)
        if self.value:
            self._normalize_tool_calls()

    def _normalize_tool_calls(self):
        tool_calls = self.value["tool_calls"]  # type: ignore
        for i in range(len(tool_calls)):
            if not isinstance(tool_calls[i], dict):
                tc = tool_calls[i]
                func_obj = getattr(tc, "function", None)
                tool_calls[i] = {
                    "id": getattr(tc, "id", None) or "",
                    "type": getattr(tc, "type", None) or "function",
                    "function": {
                        "name": getattr(func_obj, "name", None) or "",
                        "arguments": getattr(func_obj, "arguments", None) or "",
                    },
                }

    def append_value(self, value, field_name: str):
        tool_calls = self.value[field_name]  # type: ignore
        for tc_delta in value:
            idx = tc_delta.index
            while len(tool_calls) <= idx:
                tool_calls.append(
                    {
                        "id": "",
                        "type": "function",
                        "function": {"name": "", "arguments": ""},
                    }
                )
            tc = tool_calls[idx]
            if delta_id := getattr(tc_delta, "id", None):
                tc["id"] = delta_id
            if delta_type := getattr(tc_delta, "type", None):
                tc["type"] = delta_type
            if delta_func := getattr(tc_delta, "function", None):
                if name := getattr(delta_func, "name", None):
                    tc["function"]["name"] = name
                if args := getattr(delta_func, "arguments", None):
                    tc["function"]["arguments"] += args


@dataclass
class Model(EventEmitter):
    model_name: str = openai_settings.model
    _client: OpenAI = OpenAI()

    def _invoke(self, session: Session, stream=False):
        "核心方法，调用模型得到结果"
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=cast(list, session.messages),
            tools=session.tools,  # type: ignore
            stream=stream,
        )  # type: ignore
        return self._process(session, response)

    def _normalize_result_from_response(self, response: ChatCompletion):
        "将非流式的响应格式进行归一化"
        message = response.choices[0].message
        reasoning_field = _get_reasoning_field_name(message)
        result = InvokeResult(
            raw=response, message={"role": message.role, "content": ""}
        )
        message_dict = message.model_dump()
        for attr_name in [reasoning_field, "content", "tool_calls"]:
            if attr_name in message_dict:
                if message_dict[attr_name]:
                    result.message[attr_name] = message_dict[attr_name]
        return result

    def _process(
        self, session: Session, response: ChatCompletion | Stream[ChatCompletionChunk]
    ) -> InvokeResult:
        "处理响应结果"
        if isinstance(response, ChatCompletion):
            result = self._normalize_result_from_response(response)
            session.add_message(result.message)
            return result
        # 处理流式内容
        builders: list[Builder] = [
            ReasoningBuilder(self),
            ContentBuilder(self),
            ToolCallsBuilder(self),
        ]
        chunks = []
        for chunk in response:
            chunks.append(chunk)
            for b in builders:
                b.emit(chunk)
        message = {"role": "assistant", "content": ""}
        for b in builders:
            if b.value:
                for k, v in b.value.items():
                    if v is not None:
                        message[k] = v
        result = InvokeResult(raw=chunks, message=message)
        session.add_message(result.message)
        return result

    def invoke(self, session: Session):
        return self._invoke(session, stream=False)

    def invoke_stream(self, session: Session):
        return self._invoke(session, stream=True)
