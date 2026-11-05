import pytest
from httpx import AsyncClient


PRODUCTS_URL = "/api/products"


def _sku_url(product_id: int) -> str:
    return f"/api/products/{product_id}/skus"


def _sku_detail_url(sku_id: int) -> str:
    return f"/api/skus/{sku_id}"


class TestCreateSku:
    @pytest.mark.smoke
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


class TestGetSku:
    @pytest.mark.smoke
    async def test_get_found(self, async_client: AsyncClient):
        product = await _create_product(async_client, name="商品")
        sku = await _create_sku(async_client, product["id"], sku_code="B001")

        response = await async_client.get(_sku_detail_url(sku["id"]))
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["sku_code"] == "B001"
        assert data["product_id"] == product["id"]


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
