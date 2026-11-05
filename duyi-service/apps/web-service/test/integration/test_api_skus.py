import pytest
from httpx import AsyncClient


PRODUCTS_URL = "/api/products"


def _sku_url(product_id: int) -> str:
    return f"/api/products/{product_id}/skus"


def _sku_detail_url(sku_id: int) -> str:
    return f"/api/skus/{sku_id}"


def _sku_stock_url(sku_id: int) -> str:
    return f"/api/skus/{sku_id}/stock"


class TestCreateSku:
    @pytest.mark.smoke
    async def test_create_success(self, async_client: AsyncClient):
        product = await async_client.post(PRODUCTS_URL, json={"name": "测试商品"})
        product_id = product.json()["data"]["id"]

        response = await async_client.post(
            _sku_url(product_id),
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
        assert data["product_id"] == product_id


class TestListSkus:
    async def test_list_empty(self, async_client: AsyncClient):
        product = await async_client.post(PRODUCTS_URL, json={"name": "无SKU商品"})
        product_id = product.json()["data"]["id"]

        response = await async_client.get(_sku_url(product_id))
        assert response.status_code == 200
        assert response.json()["data"] == []

    async def test_list_with_data(self, async_client: AsyncClient):
        product = await async_client.post(PRODUCTS_URL, json={"name": "有SKU商品"})
        product_id = product.json()["data"]["id"]

        for code in ["A001", "A002"]:
            await async_client.post(
                _sku_url(product_id),
                json={
                    "sku_code": code,
                    "price": "99.99",
                    "attrs": {"color": "默认"},
                    "image_url": "https://example.com/img.jpg",
                },
            )

        response = await async_client.get(_sku_url(product_id))
        assert len(response.json()["data"]) == 2


class TestGetSku:
    @pytest.mark.smoke
    async def test_get_found(self, async_client: AsyncClient):
        product = await async_client.post(PRODUCTS_URL, json={"name": "商品"})
        product_id = product.json()["data"]["id"]
        sku = await async_client.post(
            _sku_url(product_id),
            json={
                "sku_code": "B001",
                "price": "99.99",
                "attrs": {"color": "红"},
                "image_url": "https://example.com/img.jpg",
            },
        )
        sku_id = sku.json()["data"]["id"]

        response = await async_client.get(_sku_detail_url(sku_id))
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["sku_code"] == "B001"
        assert data["product_id"] == product_id


class TestUpdateSku:
    async def test_update_success(self, async_client: AsyncClient):
        product = await async_client.post(PRODUCTS_URL, json={"name": "商品"})
        product_id = product.json()["data"]["id"]
        sku = await async_client.post(
            _sku_url(product_id),
            json={
                "sku_code": "C001",
                "price": "10.00",
                "attrs": {"color": "默认"},
                "image_url": "https://example.com/img.jpg",
            },
        )
        sku_id = sku.json()["data"]["id"]

        response = await async_client.put(
            _sku_detail_url(sku_id),
            json={"price": "20.00", "stock": 50},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["price"] == "20.00"
        assert data["stock"] == 50


class TestDeleteSku:
    async def test_delete_success(self, async_client: AsyncClient):
        product = await async_client.post(PRODUCTS_URL, json={"name": "商品"})
        product_id = product.json()["data"]["id"]
        sku = await async_client.post(
            _sku_url(product_id),
            json={
                "sku_code": "D001",
                "price": "99.99",
                "attrs": {"color": "默认"},
                "image_url": "https://example.com/img.jpg",
            },
        )
        sku_id = sku.json()["data"]["id"]

        response = await async_client.delete(_sku_detail_url(sku_id))
        assert response.status_code == 204


class TestUpdateStock:
    async def test_update_stock_success(self, async_client: AsyncClient):
        product = await async_client.post(PRODUCTS_URL, json={"name": "商品"})
        product_id = product.json()["data"]["id"]
        sku = await async_client.post(
            _sku_url(product_id),
            json={
                "sku_code": "E001",
                "price": "99.99",
                "stock": 10,
                "attrs": {"color": "默认"},
                "image_url": "https://example.com/img.jpg",
            },
        )
        sku_id = sku.json()["data"]["id"]

        response = await async_client.patch(
            _sku_stock_url(sku_id), params={"stock": 200}
        )
        assert response.status_code == 200
        assert response.json()["data"]["stock"] == 200
