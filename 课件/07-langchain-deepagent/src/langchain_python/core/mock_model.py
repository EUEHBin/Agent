import asyncio
import base64
import json
import mimetypes
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Literal, Sequence, Self

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.tools import BaseTool
from langgraph.runtime import get_runtime
from pydantic import BaseModel, Field

DEFAULT_CONFIG_PATH = Path(__file__).with_name("mock_model.config.jsonc")

_MODEL_CACHE: dict[str, BaseChatModel] = {}


def _strip_jsonc_comments(text: str) -> str:
    """去掉 JSONC 里的 // 和 /* */ 注释，兼容标准 json 解析。"""
    out: list[str] = []
    i = 0
    n = len(text)
    in_string = False
    while i < n:
        c = text[i]
        if in_string:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


class FakeModelError(Exception):
    """模拟模型抛出的异常，用于测试错误处理 / retry 逻辑。"""


class ToolCallConfig(BaseModel):
    name: str
    args: dict[str, Any] = Field(default_factory=dict)
    id: str | None = None


class ResponseConfig(BaseModel):
    type: Literal["message", "error", "echo_image"] = "message"
    text: str | None = None
    images: list[str] = Field(default_factory=list)
    reasoning: str | None = None
    tool_calls: list[ToolCallConfig] = Field(default_factory=list)
    message: str | None = None


class WhenConfig(BaseModel):
    last_message: Literal["human", "tool_result", "ai", "system"] | None = None
    has_image: bool | None = None
    content_contains: list[str] | None = None


class RuleConfig(BaseModel):
    when: WhenConfig
    respond: ResponseConfig
    final: ResponseConfig | None = None
    max_tool_calls: int | None = None


class FakeModelConfig(BaseModel):
    mode: Literal["cycle", "sequential", "parrot"] = "cycle"
    sleep: float = 0.0
    token_sleep: float = 0.0
    responses: list[ResponseConfig] = Field(default_factory=list)
    rules: list[RuleConfig] = Field(default_factory=list)


class ConfigFakeChatModel(BaseChatModel):
    """由 JSON 配置驱动的模拟聊天模型。

    支持的能力（全部由配置控制）：
    - 文本 / 图像 / 图文混合回复
    - 思维链（``additional_kwargs["reasoning_content"]``）
    - 工具调用（``tool_calls``）
    - 错误注入（``type: "error"``）
    - 接收并回显输入里的图像（``type: "echo_image"``）
    - 条件规则：根据最后一条消息类型 / 是否含图决定回复，
      并支持「连续调用工具 N 次后再收手」。
    """

    config: FakeModelConfig
    i: int = 0

    @property
    def _llm_type(self) -> str:
        return "config-fake-chat-model"

    def bind_tools(
        self,
        tools: Sequence[dict[str, Any] | type | Callable[..., Any] | BaseTool],
        *,
        tool_choice: str | None = None,
        **kwargs: Any,
    ) -> Self:
        """模拟模型不消费工具 schema：是否调用工具完全由配置的 ``tool_calls`` 决定。"""
        return self

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self.config.mode == "parrot":
            return self._generate_parrot(messages)
        cfg = self._select_response(messages)
        if cfg.type == "error":
            self._sleep(self.config.sleep)
            raise FakeModelError(cfg.message or "模拟模型报错")
        self._sleep_production(cfg)
        message = self._build_aimessage(cfg, messages)
        return ChatResult(generations=[ChatGeneration(message=message)])

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self.config.mode == "parrot":
            return await self._agenerate_parrot(messages)
        cfg = self._select_response(messages)
        if cfg.type == "error":
            await self._asleep(self.config.sleep)
            raise FakeModelError(cfg.message or "模拟模型报错")
        await self._asleep_production(cfg)
        message = self._build_aimessage(cfg, messages)
        return ChatResult(generations=[ChatGeneration(message=message)])

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ):
        if self.config.mode == "parrot":
            content = self._parrot_content(messages)
            if isinstance(content, str):
                yield from self._stream_text_chars(content, run_manager)
            else:
                chunk = AIMessageChunk(content=content)
                chunk.chunk_position = "last"
                gen = ChatGenerationChunk(message=chunk)
                if run_manager:
                    run_manager.on_llm_new_token("", chunk=gen)
                yield gen
            return
        cfg = self._select_response(messages)
        if cfg.type == "error":
            self._sleep(self.config.sleep)
            raise FakeModelError(cfg.message or "模拟模型报错")
        chunks = self._build_stream_chunks(cfg)
        for idx, chunk in enumerate(chunks):
            if idx == 0:
                self._sleep(self.config.sleep)
            elif self.config.token_sleep:
                self._sleep(self.config.token_sleep)
            if idx == len(chunks) - 1:
                chunk.chunk_position = "last"
            gen = ChatGenerationChunk(message=chunk)
            if run_manager:
                run_manager.on_llm_new_token(
                    chunk.content if isinstance(chunk.content, str) else "", chunk=gen
                )
            yield gen

    def _stream_text_chars(self, text: str, run_manager: Any = None):
        for idx, c in enumerate(text):
            if idx == 0:
                self._sleep(self.config.sleep)
            elif self.config.token_sleep:
                self._sleep(self.config.token_sleep)
            chunk = AIMessageChunk(content=c)
            if idx == len(text) - 1:
                chunk.chunk_position = "last"
            gen = ChatGenerationChunk(message=chunk)
            if run_manager:
                run_manager.on_llm_new_token(c, chunk=gen)
            yield gen

    async def _astream_text_chars(self, text: str, run_manager: Any = None):
        for idx, c in enumerate(text):
            if idx == 0:
                await self._asleep(self.config.sleep)
            elif self.config.token_sleep:
                await self._asleep(self.config.token_sleep)
            chunk = AIMessageChunk(content=c)
            if idx == len(text) - 1:
                chunk.chunk_position = "last"
            gen = ChatGenerationChunk(message=chunk)
            if run_manager:
                run_manager.on_llm_new_token(c, chunk=gen)
            yield gen

    def _build_stream_chunks(self, cfg: ResponseConfig) -> list[AIMessageChunk]:
        chunks: list[AIMessageChunk] = []
        if cfg.reasoning:
            chunks.extend(
                AIMessageChunk(content="", additional_kwargs={"reasoning_content": c})
                for c in cfg.reasoning
            )
        for idx, tc in enumerate(cfg.tool_calls):
            chunks.append(
                AIMessageChunk(
                    content="",
                    tool_call_chunks=[
                        {
                            "index": idx,
                            "id": self._tool_call_id(tc),
                            "name": tc.name,
                            "args": json.dumps(tc.args, ensure_ascii=False),
                        }
                    ],
                )
            )
        for img in cfg.images:
            chunks.append(
                AIMessageChunk(
                    content=[
                        {
                            "type": "image_url",
                            "image_url": {"url": self._resolve_image(img)},
                        }
                    ]
                )
            )
        if cfg.text:
            chunks.extend(AIMessageChunk(content=c) for c in cfg.text)
        return chunks

    async def _astream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ):
        if self.config.mode == "parrot":
            content = self._parrot_content(messages)
            if isinstance(content, str):
                async for chunk in self._astream_text_chars(content, run_manager):
                    yield chunk
            else:
                chunk = AIMessageChunk(content=content)
                chunk.chunk_position = "last"
                gen = ChatGenerationChunk(message=chunk)
                if run_manager:
                    run_manager.on_llm_new_token("", chunk=gen)
                yield gen
            return
        cfg = self._select_response(messages)
        if cfg.type == "error":
            await self._asleep(self.config.sleep)
            raise FakeModelError(cfg.message or "模拟模型报错")
        chunks = self._build_stream_chunks(cfg)
        for idx, chunk in enumerate(chunks):
            if idx == 0:
                await self._asleep(self.config.sleep)
            elif self.config.token_sleep:
                await self._asleep(self.config.token_sleep)
            if idx == len(chunks) - 1:
                chunk.chunk_position = "last"
            gen = ChatGenerationChunk(message=chunk)
            if run_manager:
                run_manager.on_llm_new_token(
                    chunk.content if isinstance(chunk.content, str) else "", chunk=gen
                )
            yield gen

    def _generate_parrot(self, messages: list[BaseMessage]) -> ChatResult:
        if not messages:
            raise FakeModelError("parrot 模式需要输入消息")
        content = messages[-1].content
        if isinstance(content, str):
            self._sleep_units(len(content))
        elif self.config.sleep:
            self._sleep(self.config.sleep)
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=content))]
        )

    async def _agenerate_parrot(self, messages: list[BaseMessage]) -> ChatResult:
        if not messages:
            raise FakeModelError("parrot 模式需要输入消息")
        content = messages[-1].content
        if isinstance(content, str):
            await self._asleep_units(len(content))
        elif self.config.sleep:
            await self._asleep(self.config.sleep)
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=content))]
        )

    def _sleep(self, total: float) -> None:
        """同步睡眠：供同步接口（invoke / stream）使用。"""
        if total:
            time.sleep(total)

    async def _asleep(self, total: float) -> None:
        """异步睡眠：供异步接口（ainvoke / astream）使用，不阻塞事件循环。"""
        if total:
            await asyncio.sleep(total)

    def _sleep_production(self, cfg: ResponseConfig) -> None:
        units = len(cfg.text or "") + len(cfg.reasoning or "")
        if units == 0 and (cfg.tool_calls or cfg.images):
            units = 1
        self._sleep_units(units)

    def _sleep_units(self, units: int) -> None:
        total = self.config.sleep + max(0, units - 1) * self.config.token_sleep
        self._sleep(total)

    async def _asleep_units(self, units: int) -> None:
        total = self.config.sleep + max(0, units - 1) * self.config.token_sleep
        await self._asleep(total)

    async def _asleep_production(self, cfg: ResponseConfig) -> None:
        units = len(cfg.text or "") + len(cfg.reasoning or "")
        if units == 0 and (cfg.tool_calls or cfg.images):
            units = 1
        total = self.config.sleep + max(0, units - 1) * self.config.token_sleep
        await self._asleep(total)

    @staticmethod
    def _parrot_content(messages: list[BaseMessage]) -> str | list[Any]:
        return messages[-1].content if messages else ""

    def _select_response(self, messages: list[BaseMessage]) -> ResponseConfig:
        for rule in self.config.rules:
            if not self._matches(messages, rule.when):
                continue
            if (
                rule.max_tool_calls is not None
                and messages
                and isinstance(messages[-1], ToolMessage)
            ):
                if self._count_tool_results(messages) >= rule.max_tool_calls:
                    if rule.final is not None:
                        return rule.final
                    continue
            return rule.respond
        if self.config.responses:
            return self._next_script_response()
        raise FakeModelError("没有命中的规则，且未配置 responses")

    def _next_script_response(self) -> ResponseConfig:
        if not self.config.responses:
            raise FakeModelError("未配置 responses")
        if self.config.mode == "sequential" and self.i >= len(self.config.responses):
            raise FakeModelError("sequential 模式的 responses 已用尽")
        resp = self.config.responses[self.i]
        if self.config.mode == "cycle":
            self.i = (self.i + 1) % len(self.config.responses)
        else:
            self.i += 1
        return resp

    def _matches(self, messages: list[BaseMessage], when: WhenConfig) -> bool:
        if when.last_message is not None:
            if not messages or not self._is_message_type(
                messages[-1], when.last_message
            ):
                return False
        if when.content_contains is not None:
            if not messages or not self._content_contains(
                messages[-1], when.content_contains
            ):
                return False
        if when.has_image is not None:
            if self._has_image(messages) != when.has_image:
                return False
        return True

    @staticmethod
    def _content_contains(message: BaseMessage, keywords: list[str]) -> bool:
        text = ConfigFakeChatModel._message_text(message)
        return any(kw in text for kw in keywords)

    @staticmethod
    def _message_text(message: BaseMessage) -> str:
        content = message.content
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(
                b.get("text", "")
                for b in content
                if isinstance(b, dict) and isinstance(b.get("text"), str)
            )
        return ""

    @staticmethod
    def _is_message_type(message: BaseMessage, kind: str) -> bool:
        mapping: dict[str, type] = {
            "human": HumanMessage,
            "tool_result": ToolMessage,
            "ai": AIMessage,
            "system": SystemMessage,
        }
        return isinstance(message, mapping[kind])

    @staticmethod
    def _has_image(messages: list[BaseMessage]) -> bool:
        for msg in messages:
            content = msg.content
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "image_url":
                        return True
        return False

    def _count_tool_results(self, messages: list[BaseMessage]) -> int:
        count = 0
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                break
            if isinstance(msg, ToolMessage):
                count += 1
        return count

    def _build_aimessage(
        self, cfg: ResponseConfig, messages: list[BaseMessage]
    ) -> AIMessage:
        if cfg.type == "error":
            raise FakeModelError(cfg.message or "模拟模型报错")
        if cfg.type == "echo_image":
            return self._build_echo_image(cfg, messages)
        additional_kwargs: dict[str, Any] = {}
        if cfg.reasoning:
            additional_kwargs["reasoning_content"] = cfg.reasoning
        kwargs: dict[str, Any] = {
            "content": self._build_content(cfg),
            "additional_kwargs": additional_kwargs,
        }
        if cfg.tool_calls:
            kwargs["tool_calls"] = [self._build_tool_call(tc) for tc in cfg.tool_calls]
        return AIMessage(**kwargs)

    def _build_echo_image(
        self, cfg: ResponseConfig, messages: list[BaseMessage]
    ) -> AIMessage:
        blocks: list[str | dict[str, Any]] = []
        if cfg.text:
            blocks.append({"type": "text", "text": cfg.text})
        image_block = self._find_last_image(messages)
        if image_block is not None:
            blocks.append(image_block)
        else:
            blocks.append({"type": "text", "text": "(未在输入中找到图像消息)"})
        return AIMessage(content=blocks)

    def _build_content(self, cfg: ResponseConfig) -> str | list[dict[str, Any]]:
        blocks: list[dict[str, Any]] = []
        if cfg.text:
            blocks.append({"type": "text", "text": cfg.text})
        for img in cfg.images:
            blocks.append(
                {"type": "image_url", "image_url": {"url": self._resolve_image(img)}}
            )
        if not blocks:
            return ""
        if len(blocks) == 1 and blocks[0]["type"] == "text":
            return str(blocks[0]["text"])
        return blocks

    @staticmethod
    def _build_tool_call(tc: ToolCallConfig) -> dict[str, Any]:
        return {
            "name": tc.name,
            "args": dict(tc.args),
            "id": ConfigFakeChatModel._tool_call_id(tc),
        }

    @staticmethod
    def _tool_call_id(tc: ToolCallConfig) -> str:
        return tc.id or f"call_{uuid.uuid4().hex[:16]}"

    @staticmethod
    def _resolve_image(src: str) -> str:
        if src.startswith(("http://", "https://")):
            return src
        path = Path(src)
        if path.is_file():
            mime = mimetypes.guess_type(path.name)[0] or "image/png"
            b64 = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{b64}"
        return src

    @staticmethod
    def _find_last_image(messages: list[BaseMessage]) -> dict[str, Any] | None:
        for msg in reversed(messages):
            content = msg.content
            if isinstance(content, list):
                for block in reversed(content):
                    if isinstance(block, dict) and block.get("type") == "image_url":
                        return block
        return None


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> FakeModelConfig:
    """读取并校验配置 JSONC（支持 // 与 /* */ 注释）。"""
    path = Path(config_path)
    data = json.loads(_strip_jsonc_comments(path.read_text(encoding="utf-8")))
    return FakeModelConfig.model_validate(data)


def _current_run_id() -> str | None:
    """获取当前图运行（Run）的 ID。

    在节点内通过 ``get_runtime`` 拿到运行时信息；不在图内运行
    （直接调用函数等）时可能抛异常或取不到 run_id，此时返回 None。
    """
    try:
        runtime = get_runtime()
    except RuntimeError:
        return None
    info = getattr(runtime, "execution_info", None)
    if info is None:
        return None
    return getattr(info, "run_id", None)


def mock_model(overrides: dict[str, Any] | None = None) -> BaseChatModel:
    """基于默认配置文件构造一个模拟聊天模型。

    配置路径固定为 ``mock_model.config.jsonc``，行为由配置驱动
    （文本 / 图像 / 思维链 / 工具调用 / 报错 / 条件规则）。
    是否调用工具由配置里的 ``tool_calls`` 决定，与是否绑定真实工具无关。

    每次调用都会**动态读取配置文件**，保证运行期间对配置的修改能生效。
    同时按当前图运行的 Run ID 缓存模型实例：同一个 Run 内重复创建时直接
    返回缓存的模型；不在图内运行（拿不到 run_id）时不做缓存，正常新建。

    可通过可选的字典参数覆盖**同名顶层字段**（mode / sleep / token_sleep /
    responses / rules），未覆盖的字段保持配置文件默认值，从而用同一份
    默认配置动态构造多个不同行为的模型实例。
    """
    run_id = _current_run_id()
    if run_id is not None and run_id in _MODEL_CACHE:
        return _MODEL_CACHE[run_id]
    data = load_config().model_dump()
    if overrides:
        data.update(overrides)
    model = ConfigFakeChatModel(config=FakeModelConfig.model_validate(data))
    if run_id is not None:
        _MODEL_CACHE[run_id] = model
    return model
