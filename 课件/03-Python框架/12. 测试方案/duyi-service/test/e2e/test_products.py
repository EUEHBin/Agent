import pytest
from httpx import AsyncClient


PRODUCTS_URL = "/api/products"


class TestCreateProduct:
    @pytest.mark.smoke
    async def test_create_with_required_fields(self, async_client: AsyncClient):
        response = await async_client.post(PRODUCTS_URL, json={"name": "商品A"})
        assert response.status_code == 201
        body = response.json()
        assert body["code"] == "0"
        data = body["data"]
        assert data["name"] == "商品A"
        assert data["description"] == ""
        assert data["brand"] is None
        assert data["categories"] == []
        assert data["skus"] == []


class TestGetProduct:
    @pytest.mark.smoke
    async def test_get_found(self, async_client: AsyncClient):
        product = await _create_product(async_client, name="商品X")

        response = await async_client.get(f"{PRODUCTS_URL}/{product['id']}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "商品X"


async def _create_product(client: AsyncClient, name: str) -> dict:
    response = await client.post(PRODUCTS_URL, json={"name": name})
    assert response.status_code == 201
    return response.json()["data"]
