import pytest
from httpx import AsyncClient


CATEGORIES_URL = "/api/categories"


class TestCreateCategory:
    async def test_create_with_required_fields(self, async_client: AsyncClient):
        response = await async_client.post(CATEGORIES_URL, json={"name": "电子"})
        assert response.status_code == 201
        body = response.json()
        assert body["code"] == "0"
        data = body["data"]
        assert data["name"] == "电子"
        assert data["description"] == ""

    async def test_create_with_all_fields(self, async_client: AsyncClient):
        response = await async_client.post(CATEGORIES_URL, json={
            "name": "食品",
            "description": "食品饮料分类",
        })
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "食品"
        assert data["description"] == "食品饮料分类"

    async def test_create_missing_name(self, async_client: AsyncClient):
        response = await async_client.post(CATEGORIES_URL, json={})
        assert response.status_code == 422
        assert response.json()["data"]["code"] == "422001"


class TestListCategories:
    async def test_list_empty(self, async_client: AsyncClient):
        response = await async_client.get(CATEGORIES_URL)
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        data = body["data"]
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_with_data(self, async_client: AsyncClient):
        await _create(async_client, "分类A")
        await _create(async_client, "分类B")

        response = await async_client.get(CATEGORIES_URL)
        data = response.json()["data"]
        assert len(data["items"]) == 2
        assert data["total"] == 2

    async def test_pagination(self, async_client: AsyncClient):
        for i in range(5):
            await _create(async_client, f"分类{i}")

        response = await async_client.get(CATEGORIES_URL, params={"page": 1, "page_size": 2})
        data = response.json()["data"]
        assert len(data["items"]) == 2
        assert data["total"] == 5

        response = await async_client.get(CATEGORIES_URL, params={"page": 3, "page_size": 2})
        data = response.json()["data"]
        assert len(data["items"]) == 1


class TestGetCategory:
    async def test_get_found(self, async_client: AsyncClient):
        created = await _create(async_client, "服装")

        response = await async_client.get(f"{CATEGORIES_URL}/{created['id']}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "服装"
        assert data["products"] == []

    async def test_get_not_found(self, async_client: AsyncClient):
        response = await async_client.get(f"{CATEGORIES_URL}/99999")
        assert response.status_code == 404
        assert response.json()["code"] == "404001"


class TestUpdateCategory:
    async def test_update_success(self, async_client: AsyncClient):
        created = await _create(async_client, "旧名")

        response = await async_client.put(
            f"{CATEGORIES_URL}/{created['id']}",
            json={"name": "新名"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "新名"

    async def test_update_not_found(self, async_client: AsyncClient):
        response = await async_client.put(f"{CATEGORIES_URL}/99999", json={"name": "x"})
        assert response.status_code == 404


class TestDeleteCategory:
    async def test_delete_success(self, async_client: AsyncClient, base_url: str):
        created = await _create(async_client, "待删除")

        response = await async_client.delete(f"{CATEGORIES_URL}/{created['id']}")
        assert response.status_code == 204

        async with AsyncClient(base_url=base_url) as fresh_client:
            response = await fresh_client.get(f"{CATEGORIES_URL}/{created['id']}")
            assert response.status_code == 404

    async def test_delete_not_found(self, async_client: AsyncClient):
        response = await async_client.delete(f"{CATEGORIES_URL}/99999")
        assert response.status_code == 404


async def _create(client: AsyncClient, name: str) -> dict:
    response = await client.post(CATEGORIES_URL, json={"name": name})
    assert response.status_code == 201
    return response.json()["data"]
