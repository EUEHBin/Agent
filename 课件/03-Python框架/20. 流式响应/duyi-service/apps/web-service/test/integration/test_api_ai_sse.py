import os
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.category import Category
from app.model.product import Product
from app.model.setting import Setting
from app.model.setting_group import SettingGroup
from app.model.sku import Sku
from app.model.user import User


async def _get_user_by_username(
    db_session: AsyncSession, username: str
) -> User | None:
    result = await db_session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def _mock_chat_stream_chunks(chunks: list[str]):
    for chunk in chunks:
        yield chunk


SSE_INIT_URL = "/api/ai/sse/initialize"
SSE_MESSAGE_URL = "/api/ai/sse/message"


class TestInitializeSSE:
    @pytest.mark.smoke
    async def test_requires_auth(self, async_client: AsyncClient):
        response = await async_client.get(f"{SSE_INIT_URL}/1")
        assert response.status_code == 401


class TestSendMessageSSE:
    @pytest.mark.smoke
    async def test_requires_auth(self, async_client: AsyncClient):
        response = await async_client.post(
            SSE_MESSAGE_URL,
            json={"product_id": 1, "content": "你好"},
        )
        assert response.status_code == 401
