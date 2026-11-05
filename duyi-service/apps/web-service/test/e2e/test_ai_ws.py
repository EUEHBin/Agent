import json

import pytest
from httpx import AsyncClient

CATEGORIES_URL = "/api/categories"
PRODUCTS_URL = "/api/products"
SETTINGS_URL = "/api/settings"


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


def _ws_url(base_url: str, product_id: int, token: str) -> str:
    ws_base = base_url.replace("http://", "ws://").replace("https://", "wss://")
    return f"{ws_base}/{product_id}?token={token}"


class TestAiWebSocket:
    @pytest.mark.smoke
    async def test_invalid_token_fails(self, async_client: AsyncClient):
        import websockets

        ws_url = _ws_url(str(async_client.base_url), 1, "invalid_token")
        async with websockets.connect(ws_url) as ws:
            with pytest.raises(websockets.exceptions.ConnectionClosed) as exc_info:
                await ws.recv()
            assert exc_info.value.rcvd.code == 1008  # type: ignore

    @pytest.mark.smoke
    async def test_initialize_action(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        import websockets

        product = await _prepare_test_product(async_client, auth_headers, "WS测试产品")
        token = auth_headers["Authorization"].removeprefix("Bearer ")
        ws_url = _ws_url(str(async_client.base_url), product["id"], token)

        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"action": "initialize"}))

            chunks = []
            while True:
                msg = json.loads(await ws.recv())
                if msg["type"] == "done":
                    break
                if msg["type"] == "error":
                    pytest.fail(f"WS error: {msg.get('message')}")
                assert msg["type"] == "chunk"
                chunks.append(msg["content"])

            assert len(chunks) > 0
            full_response = "".join(chunks)
            assert len(full_response) > 0

    @pytest.mark.smoke
    async def test_send_message_action(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        import websockets

        product = await _prepare_test_product(
            async_client, auth_headers, "WS消息测试产品"
        )
        token = auth_headers["Authorization"].removeprefix("Bearer ")
        ws_url = _ws_url(str(async_client.base_url), product["id"], token)

        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"action": "initialize"}))
            while True:
                msg = json.loads(await ws.recv())
                if msg["type"] == "done":
                    break

            await ws.send(
                json.dumps(
                    {"action": "send_message", "content": "这个产品有什么特点？"}
                )
            )

            chunks = []
            while True:
                msg = json.loads(await ws.recv())
                if msg["type"] == "done":
                    break
                if msg["type"] == "error":
                    pytest.fail(f"WS error: {msg.get('message')}")
                assert msg["type"] == "chunk"
                chunks.append(msg["content"])

            assert len(chunks) > 0
            full_response = "".join(chunks)
            assert len(full_response) > 0

    async def test_unknown_action_returns_error(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        import websockets

        product = await _prepare_test_product(
            async_client, auth_headers, "WS未知操作测试"
        )
        token = auth_headers["Authorization"].removeprefix("Bearer ")
        ws_url = _ws_url(str(async_client.base_url), product["id"], token)

        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"action": "invalid_action"}))
            msg = json.loads(await ws.recv())
            assert msg["type"] == "error"
            assert "未知操作" in msg["message"]

    async def test_invalid_json_returns_error(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        import websockets

        product = await _prepare_test_product(
            async_client, auth_headers, "WS无效JSON测试"
        )
        token = auth_headers["Authorization"].removeprefix("Bearer ")
        ws_url = _ws_url(str(async_client.base_url), product["id"], token)

        async with websockets.connect(ws_url) as ws:
            await ws.send("not valid json")
            msg = json.loads(await ws.recv())
            assert msg["type"] == "error"
            assert "无效的JSON格式" in msg["message"]

    async def test_empty_message_content_returns_error(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        import websockets

        product = await _prepare_test_product(
            async_client, auth_headers, "WS空消息测试"
        )
        token = auth_headers["Authorization"].removeprefix("Bearer ")
        ws_url = _ws_url(str(async_client.base_url), product["id"], token)

        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"action": "initialize"}))
            while True:
                msg = json.loads(await ws.recv())
                if msg["type"] == "done":
                    break

            await ws.send(json.dumps({"action": "send_message", "content": "   "}))
            msg = json.loads(await ws.recv())
            assert msg["type"] == "error"
            assert "消息内容不能为空" in msg["message"]
