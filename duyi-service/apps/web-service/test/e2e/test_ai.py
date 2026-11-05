import os

import pytest
from httpx import AsyncClient

CATEGORIES_URL = "/api/categories"
PRODUCTS_URL = "/api/products"
SETTINGS_URL = "/api/settings"

AI_CONVERSATION_URL = "/api/ai/conversation"
AI_SSE_INIT_URL = "/api/ai/sse/initialize"


def _ai_settings_payload() -> list[dict]:
    return [
        {"key": "ai_api_key", "value": os.environ["AI_API_KEY"]},
        {"key": "ai_base_url", "value": os.environ["AI_BASE_URL"]},
        {"key": "ai_model", "value": os.environ["AI_MODEL"]},
    ]


async def _setup_ai_settings(async_client: AsyncClient, auth_headers: dict) -> None:
    await async_client.put(
        SETTINGS_URL, headers=auth_headers, json=_ai_settings_payload()
    )


async def _create_category(async_client: AsyncClient, name: str) -> dict:
    resp = await async_client.post(CATEGORIES_URL, json={"name": name})
    assert resp.status_code == 201
    return resp.json()["data"]


async def _create_product(
    async_client: AsyncClient, name: str, category_ids: list[int] | None = None
) -> dict:
    payload = {"name": name}
    if category_ids:
        payload["category_ids"] = category_ids  # type: ignore
    resp = await async_client.post(PRODUCTS_URL, json=payload)
    assert resp.status_code == 201
    return resp.json()["data"]


async def _create_sku(
    async_client: AsyncClient, product_id: int, sku_code: str
) -> dict:
    resp = await async_client.post(
        f"{PRODUCTS_URL}/{product_id}/skus",
        json={
            "sku_code": sku_code,
            "price": "99.00",
            "stock": 100,
            "attrs": {"color": "red"},
            "image_url": "https://example.com/img.png",
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]


async def _prepare_test_product(
    async_client: AsyncClient, auth_headers: dict, product_name: str = "AI测试产品"
) -> dict:
    await _setup_ai_settings(async_client, auth_headers)
    category = await _create_category(async_client, "AI测试分类")
    product = await _create_product(
        async_client, product_name, category_ids=[category["id"]]
    )
    await _create_sku(async_client, product["id"], "AI-SKU-001")
    return product


async def _initialize_conversation(
    async_client: AsyncClient, auth_headers: dict, product_id: int
) -> str:
    full_content = ""
    async with async_client.stream(
        "GET",
        f"{AI_SSE_INIT_URL}/{product_id}",
        headers=auth_headers,
    ) as response:
        assert response.status_code == 200
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                full_content += line[6:]
    return full_content


class TestGetConversationHistory:
    @pytest.mark.smoke
    async def test_requires_auth(self, async_client: AsyncClient):
        response = await async_client.get(f"{AI_CONVERSATION_URL}/1")
        assert response.status_code == 401

    async def test_empty_when_no_conversation(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        response = await async_client.get(
            f"{AI_CONVERSATION_URL}/1", headers=auth_headers
        )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        assert body["data"] == []

    @pytest.mark.smoke
    async def test_returns_history_after_initialize(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        product = await _prepare_test_product(async_client, auth_headers)
        await _initialize_conversation(async_client, auth_headers, product["id"])

        response = await async_client.get(
            f"{AI_CONVERSATION_URL}/{product['id']}", headers=auth_headers
        )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        data = body["data"]
        assert len(data) == 1
        assert data[0]["role"] == "assistant"
        assert len(data[0]["content"]) > 0


class TestDeleteConversation:
    @pytest.mark.smoke
    async def test_requires_auth(self, async_client: AsyncClient):
        response = await async_client.delete(f"{AI_CONVERSATION_URL}/1")
        assert response.status_code == 401

    async def test_deletes_conversation(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        product = await _prepare_test_product(async_client, auth_headers)
        await _initialize_conversation(async_client, auth_headers, product["id"])

        response = await async_client.delete(
            f"{AI_CONVERSATION_URL}/{product['id']}", headers=auth_headers
        )
        assert response.status_code == 204

        response = await async_client.get(
            f"{AI_CONVERSATION_URL}/{product['id']}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["data"] == []

    async def test_noop_when_no_conversation(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        response = await async_client.delete(
            f"{AI_CONVERSATION_URL}/99999", headers=auth_headers
        )
        assert response.status_code == 204
