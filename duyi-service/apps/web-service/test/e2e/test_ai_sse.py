import pytest
from httpx import AsyncClient

CATEGORIES_URL = "/api/categories"
PRODUCTS_URL = "/api/products"
SETTINGS_URL = "/api/settings"

SSE_INIT_URL = "/api/ai/sse/initialize"
SSE_MESSAGE_URL = "/api/ai/sse/message"


def _ai_settings_payload() -> list[dict]:
    return [
        {"key": "ai_api_key", "value": "mock-api-key"},
        {"key": "ai_base_url", "value": "http://localhost:18001"},
        {"key": "ai_model", "value": "mock-model"},
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


async def _consume_sse_stream(response) -> str:
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    full_content = ""
    is_error_event = False
    async for line in response.aiter_lines():
        if line.startswith("event: error"):
            is_error_event = True
        elif line.startswith("data: "):
            if not is_error_event:
                full_content += line[6:]
            is_error_event = False
    return full_content


async def _consume_sse_error(response) -> str | None:
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    is_error = False
    async for line in response.aiter_lines():
        if line.startswith("event: error"):
            is_error = True
        elif line.startswith("data: ") and is_error:
            return line[6:]
    return None


class TestInitializeSSE:
    @pytest.mark.smoke
    async def test_requires_auth(self, async_client: AsyncClient):
        response = await async_client.get(f"{SSE_INIT_URL}/1")
        assert response.status_code == 401

    @pytest.mark.smoke
    async def test_initialize_returns_sse_stream(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        product = await _prepare_test_product(async_client, auth_headers)

        async with async_client.stream(
            "GET",
            f"{SSE_INIT_URL}/{product['id']}",
            headers=auth_headers,
        ) as response:
            content = await _consume_sse_stream(response)
            assert len(content) > 0

    async def test_initialize_contains_product_info(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        product = await _prepare_test_product(
            async_client, auth_headers, product_name="SSE测试产品"
        )

        async with async_client.stream(
            "GET",
            f"{SSE_INIT_URL}/{product['id']}",
            headers=auth_headers,
        ) as response:
            content = await _consume_sse_stream(response)
            assert "Mock AI回应" in content

    async def test_initialize_nonexistent_product_returns_error(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        await _setup_ai_settings(async_client, auth_headers)

        async with async_client.stream(
            "GET",
            f"{SSE_INIT_URL}/99999",
            headers=auth_headers,
        ) as response:
            error_msg = await _consume_sse_error(response)
            assert error_msg is not None
            assert len(error_msg) > 0

    async def test_initialize_twice_returns_error(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        product = await _prepare_test_product(async_client, auth_headers)

        async with async_client.stream(
            "GET",
            f"{SSE_INIT_URL}/{product['id']}",
            headers=auth_headers,
        ) as response:
            await _consume_sse_stream(response)

        async with async_client.stream(
            "GET",
            f"{SSE_INIT_URL}/{product['id']}",
            headers=auth_headers,
        ) as response:
            error_msg = await _consume_sse_error(response)
            assert error_msg is not None
            assert "已有对话历史" in error_msg


class TestSendMessageSSE:
    async def _prepare_and_init(
        self, async_client: AsyncClient, auth_headers: dict
    ) -> dict:
        product = await _prepare_test_product(
            async_client, auth_headers, "SSE消息测试产品"
        )

        async with async_client.stream(
            "GET",
            f"{SSE_INIT_URL}/{product['id']}",
            headers=auth_headers,
        ) as response:
            await _consume_sse_stream(response)

        return product

    @pytest.mark.smoke
    async def test_requires_auth(self, async_client: AsyncClient):
        response = await async_client.post(
            SSE_MESSAGE_URL,
            json={"product_id": 1, "content": "你好"},
        )
        assert response.status_code == 401

    @pytest.mark.smoke
    async def test_send_message_returns_sse_stream(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        product = await self._prepare_and_init(async_client, auth_headers)

        async with async_client.stream(
            "POST",
            SSE_MESSAGE_URL,
            headers=auth_headers,
            json={"product_id": product["id"], "content": "这个产品怎么样？"},
        ) as response:
            content = await _consume_sse_stream(response)
            assert len(content) > 0

    async def test_send_message_without_init_returns_error(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        product = await _prepare_test_product(
            async_client, auth_headers, "未初始化产品"
        )

        async with async_client.stream(
            "POST",
            SSE_MESSAGE_URL,
            headers=auth_headers,
            json={"product_id": product["id"], "content": "你好"},
        ) as response:
            error_msg = await _consume_sse_error(response)
            assert error_msg is not None
            assert "未找到对话记录" in error_msg
