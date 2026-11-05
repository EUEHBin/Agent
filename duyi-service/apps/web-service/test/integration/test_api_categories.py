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
        assert body["data"]["name"] == "电子"
        assert body["data"]["description"] == ""

    async def test_create_with_all_fields(self, async_client: AsyncClient):
        response = await async_client.post(
            CATEGORIES_URL, json={"name": "食品", "description": "食品饮料分类"}
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "食品"
        assert data["description"] == "食品饮料分类"


class TestListCategories:
    async def test_list_empty(self, async_client: AsyncClient):
        response = await async_client.get(CATEGORIES_URL)
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        assert body["data"]["items"] == []
        assert body["data"]["total"] == 0

    async def test_list_with_data(self, async_client: AsyncClient):
        await async_client.post(CATEGORIES_URL, json={"name": "A"})
        await async_client.post(CATEGORIES_URL, json={"name": "B"})

        response = await async_client.get(CATEGORIES_URL)
        data = response.json()["data"]
        assert len(data["items"]) == 2
        assert data["total"] == 2

    async def test_pagination(self, async_client: AsyncClient):
        for i in range(5):
            await async_client.post(CATEGORIES_URL, json={"name": f"分类{i}"})

        response = await async_client.get(CATEGORIES_URL, params={"page": 1, "page_size": 2})
        data = response.json()["data"]
        assert len(data["items"]) == 2
        assert data["total"] == 5

        response = await async_client.get(CATEGORIES_URL, params={"page": 3, "page_size": 2})
        data = response.json()["data"]
        assert len(data["items"]) == 1


class TestGetCategory:
    @pytest.mark.smoke
    async def test_get_found(self, async_client: AsyncClient):
        created = await async_client.post(CATEGORIES_URL, json={"name": "服装"})
        cat_id = created.json()["data"]["id"]

        response = await async_client.get(f"{CATEGORIES_URL}/{cat_id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "服装"
        assert data["products"] == []


class TestUpdateCategory:
    async def test_update_success(self, async_client: AsyncClient):
        created = await async_client.post(CATEGORIES_URL, json={"name": "旧名"})
        cat_id = created.json()["data"]["id"]

        response = await async_client.put(f"{CATEGORIES_URL}/{cat_id}", json={"name": "新名"})
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "新名"


class TestDeleteCategory:
    async def test_delete_success(self, async_client: AsyncClient):
        created = await async_client.post(CATEGORIES_URL, json={"name": "待删除"})
        cat_id = created.json()["data"]["id"]

        response = await async_client.delete(f"{CATEGORIES_URL}/{cat_id}")
        assert response.status_code == 204
