import pytest
from httpx import AsyncClient


CATEGORIES_URL = "/api/categories"


class TestCreateCategory:
    @pytest.mark.smoke
    async def test_create_with_required_fields(self, async_client: AsyncClient):
        response = await async_client.post(CATEGORIES_URL, json={"name": "电子"})
        assert response.status_code == 201
        body = response.json()
        assert body["code"] == "0"
        data = body["data"]
        assert data["name"] == "电子"
        assert data["description"] == ""


class TestGetCategory:
    @pytest.mark.smoke
    async def test_get_found(self, async_client: AsyncClient):
        created = await _create(async_client, "服装")

        response = await async_client.get(f"{CATEGORIES_URL}/{created['id']}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "服装"
        assert data["products"] == []


async def _create(client: AsyncClient, name: str) -> dict:
    response = await client.post(CATEGORIES_URL, json={"name": name})
    assert response.status_code == 201
    return response.json()["data"]
