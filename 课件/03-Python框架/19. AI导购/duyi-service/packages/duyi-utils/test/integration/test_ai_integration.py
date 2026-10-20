"""集成测试：使用真实的 AI API 进行测试。

要求：
  在项目根目录提供 .env.test 文件，包含 AI_API_KEY / AI_BASE_URL / AI_MODEL。
"""

import os

import pytest
from dotenv import load_dotenv

from duyi_utils.ai.chat import AIChat, AIChatConfig, AIMessage, MessageRole

load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", ".env.test"
    )
)


@pytest.fixture(scope="module")
def config():
    api_key = os.environ.get("AI_API_KEY")
    if not api_key:
        pytest.skip("AI_API_KEY 未设置，跳过集成测试")

    return AIChatConfig(
        api_key=api_key,
        base_url=os.environ.get("AI_BASE_URL", "https://api.openai.com/v1"),
        model=os.environ.get("AI_MODEL", "gpt-4o"),
    )


@pytest.fixture(scope="module")
def chat(config):
    return AIChat(config)


class TestChatStreamIntegration:
    async def test_returns_text_response(self, chat):
        messages = [
            AIMessage(role=MessageRole.USER, content="请用中文回复：你好"),
        ]

        full_response = ""
        async for text in chat.chat_stream(messages):
            full_response += text

        assert len(full_response) > 0

    async def test_multi_turn_conversation(self, chat):
        messages = [
            AIMessage(
                role=MessageRole.SYSTEM,
                content="你是一个助手，回复必须极其简短，不超过10个字。",
            ),
            AIMessage(role=MessageRole.USER, content="1+1等于几？"),
        ]

        full_response = ""
        async for text in chat.chat_stream(messages):
            full_response += text

        assert len(full_response) > 0

    async def test_stream_returns_multiple_chunks(self, chat):
        messages = [
            AIMessage(role=MessageRole.USER, content="请介绍一下人工智能的发展历史，用中文回答。"),
        ]

        chunk_count = 0
        async for _ in chat.chat_stream(messages):
            chunk_count += 1

        assert chunk_count > 1
