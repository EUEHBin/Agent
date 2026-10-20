from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.ai import AiException
from app.model.ai_conversation import AiConversation
from app.model.category import Category
from app.model.product import Product
from app.model.setting import Setting
from app.model.setting_group import SettingGroup
from app.model.sku import Sku
from app.model.user import User
from app.service.ai_service import (
    AiService,
    MESSAGE_ROLE_ASSISTANT,
    MESSAGE_ROLE_SYSTEM,
    MESSAGE_ROLE_USER,
)
from duyi_utils.auth.password import hash_password  # type: ignore[import-untyped]


def _default_password_hash() -> str:
    return hash_password("test123456")


async def _create_user(db_session: AsyncSession, username: str) -> User:
    user = User(username=username, password_hash=_default_password_hash())
    db_session.add(user)
    await db_session.flush()
    return user


async def _create_setting_group(db_session: AsyncSession, key: str) -> SettingGroup:
    group = SettingGroup(key=key, display_name=key, description="")
    db_session.add(group)
    await db_session.flush()
    return group


async def _create_setting(
    db_session: AsyncSession, group_id: int, key: str, value: str
) -> Setting:
    setting = Setting(key=key, value=value, group_id=group_id)
    db_session.add(setting)
    await db_session.flush()
    return setting


async def _seed_ai_settings(db_session: AsyncSession) -> None:
    import os

    group = await _create_setting_group(db_session, "ai")
    await _create_setting(db_session, group.id, "ai_api_key", os.environ["AI_API_KEY"])
    await _create_setting(
        db_session, group.id, "ai_base_url", os.environ["AI_BASE_URL"]
    )
    await _create_setting(db_session, group.id, "ai_model", os.environ["AI_MODEL"])


async def _create_product_with_category_and_sku(
    db_session: AsyncSession, name: str = "测试产品"
) -> Product:
    cat = Category(name="测试分类")
    db_session.add(cat)
    await db_session.flush()

    product = Product(name=name, description="产品描述", brand="测试品牌")
    product.categories.append(cat)
    db_session.add(product)
    await db_session.flush()

    sku = Sku(
        product_id=product.id,
        sku_code="TEST-001",
        price=Decimal("99.00"),
        stock=100,
        attrs={"color": "red"},
        image_url="https://example.com/img.png",
    )
    db_session.add(sku)
    await db_session.flush()
    return product


async def _create_conversation(
    db_session: AsyncSession,
    user_id: int,
    product_id: int,
    messages: list[dict] | None = None,
) -> AiConversation:
    conv = AiConversation(
        user_id=user_id,
        product_id=product_id,
        messages=messages or [],
    )
    db_session.add(conv)
    await db_session.flush()
    return conv


async def _get_conversation(
    db_session: AsyncSession, user_id: int, product_id: int
) -> AiConversation | None:
    result = await db_session.execute(
        select(AiConversation).where(
            AiConversation.user_id == user_id,
            AiConversation.product_id == product_id,
        )
    )
    return result.scalar_one_or_none()


async def _mock_chat_stream_chunks(chunks: list[str]):
    for chunk in chunks:
        yield chunk


class TestGetHistory:
    @pytest.mark.smoke
    async def test_returns_empty_when_no_conversation(self, db_session: AsyncSession):
        svc = AiService(db_session)
        result = await svc.get_history(user_id=1, product_id=1)
        assert result == []

    async def test_returns_messages_without_system(self, db_session: AsyncSession):
        user = await _create_user(db_session, "history_user")
        product = await _create_product_with_category_and_sku(db_session)
        await _create_conversation(
            db_session,
            user.id,
            product.id,
            messages=[
                {"role": MESSAGE_ROLE_SYSTEM, "content": "system prompt"},
                {"role": MESSAGE_ROLE_USER, "content": "用户问题"},
                {"role": MESSAGE_ROLE_ASSISTANT, "content": "AI回答"},
            ],
        )

        svc = AiService(db_session)
        result = await svc.get_history(user.id, product.id)

        assert len(result) == 2
        assert result[0]["role"] == MESSAGE_ROLE_USER
        assert result[0]["content"] == "用户问题"
        assert result[1]["role"] == MESSAGE_ROLE_ASSISTANT
        assert result[1]["content"] == "AI回答"


class TestInitialize:
    async def _setup_for_initialize(
        self, db_session: AsyncSession, username: str = "init_user"
    ) -> tuple[int, int]:
        user = await _create_user(db_session, username)
        await _seed_ai_settings(db_session)
        product = await _create_product_with_category_and_sku(db_session)
        return user.id, product.id

    @pytest.mark.smoke
    async def test_create_new_conversation(self, db_session: AsyncSession):
        user_id, product_id = await self._setup_for_initialize(db_session)

        mock_instance = MagicMock()
        mock_instance.chat_stream = lambda messages: _mock_chat_stream_chunks(
            ["你好，这是测试产品"]
        )

        svc = AiService(db_session)
        with patch("app.service.ai_service.AIChat", return_value=mock_instance):
            full_response = ""
            async for chunk in svc.initialize(user_id, product_id):
                full_response += chunk

        assert full_response == "你好，这是测试产品"
        conv = await _get_conversation(db_session, user_id, product_id)
        assert conv is not None
        assert len(conv.messages) == 2
        assert conv.messages[0]["role"] == MESSAGE_ROLE_SYSTEM
        assert (
            "测试产品" in conv.messages[0]["content"]
        )  # system prompt contains product info
        assert conv.messages[1]["role"] == MESSAGE_ROLE_ASSISTANT
        assert conv.messages[1]["content"] == "你好，这是测试产品"

    async def test_raises_when_conversation_already_has_messages(
        self, db_session: AsyncSession
    ):
        user_id, product_id = await self._setup_for_initialize(db_session)
        await _create_conversation(
            db_session,
            user_id,
            product_id,
            messages=[
                {"role": MESSAGE_ROLE_SYSTEM, "content": "old system prompt"},
                {"role": MESSAGE_ROLE_ASSISTANT, "content": "old ai response"},
            ],
        )

        svc = AiService(db_session)
        with pytest.raises(AiException) as exc:
            async for _ in svc.initialize(user_id, product_id):
                pass

        assert "已有对话历史记录" in str(exc.value.message)

    async def test_reinitialize_empty_conversation(self, db_session: AsyncSession):
        user_id, product_id = await self._setup_for_initialize(db_session)
        await _create_conversation(db_session, user_id, product_id, messages=[])

        mock_instance = MagicMock()
        mock_instance.chat_stream = lambda messages: _mock_chat_stream_chunks(
            ["新的介绍"]
        )

        svc = AiService(db_session)
        with patch("app.service.ai_service.AIChat", return_value=mock_instance):
            full_response = ""
            async for chunk in svc.initialize(user_id, product_id):
                full_response += chunk

        assert full_response == "新的介绍"
        conv = await _get_conversation(db_session, user_id, product_id)
        assert conv is not None
        assert len(conv.messages) == 2
        assert conv.messages[1]["content"] == "新的介绍"

    async def test_system_prompt_contains_product_info(self, db_session: AsyncSession):
        user_id, product_id = await self._setup_for_initialize(db_session)

        mock_instance = MagicMock()
        mock_instance.chat_stream = lambda messages: _mock_chat_stream_chunks(
            ["AI回复"]
        )

        svc = AiService(db_session)
        with patch("app.service.ai_service.AIChat", return_value=mock_instance):
            async for _ in svc.initialize(user_id, product_id):
                pass

        conv = await _get_conversation(db_session, user_id, product_id)
        assert conv is not None
        system_prompt = conv.messages[0]["content"]
        assert "测试产品" in system_prompt
        assert "测试品牌" in system_prompt
        assert "产品描述" in system_prompt
        assert "测试分类" in system_prompt
        assert "TEST-001" in system_prompt

    async def test_raises_when_ai_config_incomplete(self, db_session: AsyncSession):
        user = await _create_user(db_session, "noconfig_user")
        product = await _create_product_with_category_and_sku(db_session)

        svc = AiService(db_session)
        with pytest.raises(AiException) as exc:
            async for _ in svc.initialize(user.id, product.id):
                pass

        assert "AI服务配置不完整" in str(exc.value.message)


class TestSendMessageStream:
    async def _setup_for_stream(
        self, db_session: AsyncSession, username: str = "stream_user"
    ) -> tuple[int, int]:
        user = await _create_user(db_session, username)
        await _seed_ai_settings(db_session)
        product = await _create_product_with_category_and_sku(db_session)

        mock_instance = MagicMock()
        mock_instance.chat_stream = lambda messages: _mock_chat_stream_chunks(
            ["初始介绍"]
        )
        svc = AiService(db_session)
        with patch("app.service.ai_service.AIChat", return_value=mock_instance):
            async for _ in svc.initialize(user.id, product.id):
                pass

        return user.id, product.id

    @pytest.mark.smoke
    async def test_sends_message_and_updates_conversation(
        self, db_session: AsyncSession
    ):
        user_id, product_id = await self._setup_for_stream(db_session)

        mock_instance = MagicMock()
        mock_instance.chat_stream = lambda messages: _mock_chat_stream_chunks(
            ["这是", "AI", "回复"]
        )

        svc = AiService(db_session)
        with patch("app.service.ai_service.AIChat", return_value=mock_instance):
            full_response = ""
            async for chunk in svc.send_message_stream(user_id, product_id, "用户问题"):
                full_response += chunk

        assert full_response == "这是AI回复"

        conv = await _get_conversation(db_session, user_id, product_id)
        assert conv is not None
        assert len(conv.messages) == 4  # system + init assistant + user + new assistant
        assert conv.messages[2]["role"] == MESSAGE_ROLE_USER
        assert conv.messages[2]["content"] == "用户问题"
        assert conv.messages[3]["role"] == MESSAGE_ROLE_ASSISTANT
        assert conv.messages[3]["content"] == "这是AI回复"

    async def test_raises_when_no_conversation(self, db_session: AsyncSession):
        svc = AiService(db_session)
        with pytest.raises(AiException) as exc:
            async for _ in svc.send_message_stream(1, 1, "你好"):
                pass

        assert "未找到对话记录" in str(exc.value.message)


class TestDeleteConversation:
    @pytest.mark.smoke
    async def test_deletes_existing_conversation(self, db_session: AsyncSession):
        user = await _create_user(db_session, "delete_user")
        product = await _create_product_with_category_and_sku(db_session)
        conv = await _create_conversation(
            db_session,
            user.id,
            product.id,
            messages=[
                {"role": MESSAGE_ROLE_SYSTEM, "content": "prompt"},
                {"role": MESSAGE_ROLE_ASSISTANT, "content": "reply"},
            ],
        )

        svc = AiService(db_session)
        await svc.delete_conversation(user.id, product.id)

        result = await _get_conversation(db_session, user.id, product.id)
        assert result is None

    async def test_noop_when_no_conversation(self, db_session: AsyncSession):
        svc = AiService(db_session)
        await svc.delete_conversation(user_id=99999, product_id=99999)
