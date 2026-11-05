from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from duyi_utils.ai.chat import AIChat, AIChatConfig, AIMessage, MessageRole


@pytest.fixture
def config():
    return AIChatConfig(
        api_key="test-key",
        base_url="https://test.api.com/v1",
        model="test-model",
    )


@pytest.fixture
def chat(config):
    with patch("duyi_utils.ai.chat.AsyncOpenAI") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        return AIChat(config)


class TestAIChatConfig:
    def test_defaults(self):
        config = AIChatConfig(api_key="sk-xxx")
        assert config.api_key == "sk-xxx"
        assert config.base_url == "https://api.openai.com/v1"
        assert config.model == "gpt-4o"


class TestAIMessage:
    def test_create_message(self):
        msg = AIMessage(role=MessageRole.USER, content="你好")
        assert msg.role == MessageRole.USER
        assert msg.content == "你好"

    def test_system_message(self):
        msg = AIMessage(role=MessageRole.SYSTEM, content="你是助手")
        assert msg.role == MessageRole.SYSTEM
        assert msg.role.value == "system"

    def test_assistant_message(self):
        msg = AIMessage(role=MessageRole.ASSISTANT, content="好的")
        assert msg.role == MessageRole.ASSISTANT
        assert msg.role.value == "assistant"


class TestMessageRole:
    def test_values(self):
        assert MessageRole.SYSTEM == "system"
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"

    def test_is_string(self):
        assert isinstance(MessageRole.USER, str)


class TestChatStream:
    @staticmethod
    def _make_chunk(content):
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta = MagicMock()
        chunk.choices[0].delta.content = content
        return chunk

    @staticmethod
    def _make_async_stream(chunks):
        async def _stream():
            for chunk in chunks:
                yield chunk

        return _stream()

    async def test_yields_content(self, chat):
        chunks = [
            self._make_chunk("你好"),
            self._make_chunk("，世界"),
            self._make_chunk("！"),
        ]
        chat._client.chat.completions.create = AsyncMock(
            return_value=self._make_async_stream(chunks)
        )

        messages = [AIMessage(role=MessageRole.USER, content="hello")]
        result = []
        async for text in chat.chat_stream(messages):
            result.append(text)

        assert result == ["你好", "，世界", "！"]

    async def test_passes_model_and_messages(self, chat):
        chunk = self._make_chunk("ok")
        chat._client.chat.completions.create = AsyncMock(
            return_value=self._make_async_stream([chunk])
        )

        messages = [
            AIMessage(role=MessageRole.SYSTEM, content="system prompt"),
            AIMessage(role=MessageRole.USER, content="user message"),
        ]

        async for _ in chat.chat_stream(messages):
            pass

        call_kwargs = chat._client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "test-model"
        assert call_kwargs["stream"] is True
        assert call_kwargs["messages"] == [
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "user message"},
        ]

    async def test_skips_empty_delta_content(self, chat):
        chunks = [
            self._make_chunk(None),
            self._make_chunk("hello"),
            self._make_chunk(None),
            self._make_chunk(" world"),
        ]
        chat._client.chat.completions.create = AsyncMock(
            return_value=self._make_async_stream(chunks)
        )

        messages = [AIMessage(role=MessageRole.USER, content="hi")]
        result = []
        async for text in chat.chat_stream(messages):
            result.append(text)

        assert result == ["hello", " world"]

    async def test_empty_messages(self, chat):
        chunk = self._make_chunk("ok")
        chat._client.chat.completions.create = AsyncMock(
            return_value=self._make_async_stream([chunk])
        )

        async for _ in chat.chat_stream([]):
            pass

        call_kwargs = chat._client.chat.completions.create.call_args.kwargs
        assert call_kwargs["messages"] == []
