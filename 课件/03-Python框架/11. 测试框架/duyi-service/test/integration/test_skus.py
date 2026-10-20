import pytest
from httpx import AsyncClient


PRODUCTS_URL = "/api/products"
CATEGORIES_URL = "/api/categories"


def _sku_url(product_id: int) -> str:
    return f"/api/products/{product_id}/skus"


def _sku_detail_url(sku_id: int) -> str:
    return f"/api/skus/{sku_id}"


def _sku_stock_url(sku_id: int) -> str:
    return f"/api/skus/{sku_id}/stock"


class TestCreateSku:
    async def test_create_success(self, async_client: AsyncClient):
        product = await _create_product(async_client, name="测试商品")

        response = await async_client.post(
            _sku_url(product["id"]),
            json={
                "sku_code": "SKU-001",
                "price": "99.99",
                "stock": 100,
                "attrs": {"color": "红色", "size": "L"},
                "image_url": "https://example.com/img.jpg",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["code"] == "0"
        data = body["data"]
        assert data["sku_code"] == "SKU-001"
        assert data["price"] == "99.99"
        assert data["stock"] == 100
        assert data["attrs"] == {"color": "红色", "size": "L"}
        assert data["product_id"] == product["id"]

    async def test_create_product_not_found(self, async_client: AsyncClient):
        response = await async_client.post(
            _sku_url(99999),
            json={
                "sku_code": "SKU-002",
                "price": "50.00",
                "attrs": {"color": "蓝"},
                "image_url": "https://example.com/img.jpg",
            },
        )
        assert response.status_code == 404
        assert response.json()["code"] == "404001"

    async def test_create_duplicate_sku_code(self, async_client: AsyncClient):
        product = await _create_product(async_client, name="商品")

        payload = {
            "sku_code": "SKU-DUP",
            "price": "10.00",
            "attrs": {"size": "M"},
            "image_url": "https://example.com/img.jpg",
        }
        await async_client.post(_sku_url(product["id"]), json=payload)

        response = await async_client.post(_sku_url(product["id"]), json=payload)
        assert response.status_code == 422
        assert response.json()["code"] == "422002"


class TestListSkus:
    async def test_list_empty(self, async_client: AsyncClient):
        product = await _create_product(async_client, name="无SKU商品")

        response = await async_client.get(_sku_url(product["id"]))
        assert response.status_code == 200
        data = response.json()["data"]
        assert data == []

    async def test_list_with_data(self, async_client: AsyncClient):
        product = await _create_product(async_client, name="有SKU商品")
        await _create_sku(async_client, product["id"], sku_code="A001")
        await _create_sku(async_client, product["id"], sku_code="A002")

        response = await async_client.get(_sku_url(product["id"]))
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2


class TestGetSku:
    async def test_get_found(self, async_client: AsyncClient):
        product = await _create_product(async_client, name="商品")
        sku = await _create_sku(async_client, product["id"], sku_code="B001")

        response = await async_client.get(_sku_detail_url(sku["id"]))
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["sku_code"] == "B001"
        assert data["product_id"] == product["id"]

    async def test_get_not_found(self, async_client: AsyncClient):
        response = await async_client.get(_sku_detail_url(99999))
        assert response.status_code == 404
        assert response.json()["code"] == "404001"


class TestUpdateSku:
    async def test_update_success(self, async_client: AsyncClient):
        product = await _create_product(async_client, name="商品")
        sku = await _create_sku(async_client, product["id"], sku_code="C001", price="10.00")

        response = await async_client.put(
            _sku_detail_url(sku["id"]),
            json={"price": "20.00", "stock": 50},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["price"] == "20.00"
        assert data["stock"] == 50
        assert data["sku_code"] == "C001"

    async def test_update_not_found(self, async_client: AsyncClient):
        response = await async_client.put(_sku_detail_url(99999), json={"price": "1.00"})
        assert response.status_code == 404


class TestDeleteSku:
    async def test_delete_success(self, async_client: AsyncClient, base_url: str):
        product = await _create_product(async_client, name="商品")
        sku = await _create_sku(async_client, product["id"], sku_code="D001")

        response = await async_client.delete(_sku_detail_url(sku["id"]))
        assert response.status_code == 204

        async with AsyncClient(base_url=base_url) as fresh_client:
            response = await fresh_client.get(_sku_detail_url(sku["id"]))
            assert response.status_code == 404

    async def test_delete_not_found(self, async_client: AsyncClient):
        response = await async_client.delete(_sku_detail_url(99999))
        assert response.status_code == 404


class TestUpdateStock:
    async def test_update_stock_success(self, async_client: AsyncClient):
        product = await _create_product(async_client, name="商品")
        sku = await _create_sku(async_client, product["id"], sku_code="E001", stock=10)

        response = await async_client.patch(
            _sku_stock_url(sku["id"]),
            params={"stock": 200},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["stock"] == 200

    async def test_update_stock_negative(self, async_client: AsyncClient):
        product = await _create_product(async_client, name="商品")
        sku = await _create_sku(async_client, product["id"], sku_code="E002")

        response = await async_client.patch(
            _sku_stock_url(sku["id"]),
            params={"stock": -1},
        )
        assert response.status_code == 422

    async def test_update_stock_not_found(self, async_client: AsyncClient):
        response = await async_client.patch(
            _sku_stock_url(99999),
            params={"stock": 100},
        )
        assert response.status_code == 404


# ─── 辅助函数 ───


async def _create_product(client: AsyncClient, name: str) -> dict:
    response = await client.post(PRODUCTS_URL, json={"name": name})
    assert response.status_code == 201
    return response.json()["data"]


async def _create_sku(
    client: AsyncClient, product_id: int, sku_code: str, price: str = "99.99", stock: int = 0
) -> dict:
    response = await client.post(
        _sku_url(product_id),
        json={
            "sku_code": sku_code,
            "price": price,
            "stock": stock,
            "attrs": {"color": "默认"},
            "image_url": "https://example.com/img.jpg",
        },
    )
    assert response.status_code == 201
    return response.json()["data"]
