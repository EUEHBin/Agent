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

    async def test_create_with_all_fields(self, async_client: AsyncClient):
        response = await async_client.post(
            PRODUCTS_URL,
            json={"name": "商品B", "description": "描述B", "brand": "品牌B"},
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "商品B"
        assert data["description"] == "描述B"
        assert data["brand"] == "品牌B"

    async def test_create_with_categories(self, async_client: AsyncClient):
        cat_resp = await async_client.post("/api/categories", json={"name": "分类1"})
        cat_id = cat_resp.json()["data"]["id"]

        response = await async_client.post(
            PRODUCTS_URL,
            json={"name": "商品C", "category_ids": [cat_id]},
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert len(data["categories"]) == 1
        assert data["categories"][0]["name"] == "分类1"


class TestListProducts:
    async def test_list_empty(self, async_client: AsyncClient):
        response = await async_client.get(PRODUCTS_URL)
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        data = body["data"]
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 20

    async def test_list_with_data(self, async_client: AsyncClient):
        await async_client.post(PRODUCTS_URL, json={"name": "商品1"})
        await async_client.post(PRODUCTS_URL, json={"name": "商品2"})

        response = await async_client.get(PRODUCTS_URL)
        data = response.json()["data"]
        assert len(data["items"]) == 2
        assert data["total"] == 2

    async def test_pagination(self, async_client: AsyncClient):
        for i in range(5):
            await async_client.post(PRODUCTS_URL, json={"name": f"商品{i}"})

        response = await async_client.get(PRODUCTS_URL, params={"page": 1, "page_size": 2})
        data = response.json()["data"]
        assert len(data["items"]) == 2
        assert data["total"] == 5

        response = await async_client.get(PRODUCTS_URL, params={"page": 3, "page_size": 2})
        data = response.json()["data"]
        assert len(data["items"]) == 1

    async def test_filter_by_keyword(self, async_client: AsyncClient):
        await async_client.post(PRODUCTS_URL, json={"name": "苹果手机", "description": "高端智能手机"})
        await async_client.post(PRODUCTS_URL, json={"name": "华为手机", "description": "国产旗舰"})
        await async_client.post(PRODUCTS_URL, json={"name": "香蕉", "description": "水果"})

        response = await async_client.get(PRODUCTS_URL, params={"keyword": "手机"})
        data = response.json()["data"]
        assert data["total"] == 2

    async def test_filter_by_brand(self, async_client: AsyncClient):
        await async_client.post(PRODUCTS_URL, json={"name": "产品A", "brand": "Apple"})
        await async_client.post(PRODUCTS_URL, json={"name": "产品B", "brand": "华为"})
        await async_client.post(PRODUCTS_URL, json={"name": "产品C", "brand": "Apple"})

        response = await async_client.get(PRODUCTS_URL, params={"brand": "Apple"})
        data = response.json()["data"]
        assert data["total"] == 2

    async def test_filter_by_category(self, async_client: AsyncClient):
        c1 = await async_client.post("/api/categories", json={"name": "电子"})
        c1_id = c1.json()["data"]["id"]
        c2 = await async_client.post("/api/categories", json={"name": "食品"})
        c2_id = c2.json()["data"]["id"]

        await async_client.post(PRODUCTS_URL, json={"name": "笔记本", "category_ids": [c1_id]})
        await async_client.post(PRODUCTS_URL, json={"name": "手机", "category_ids": [c1_id]})
        await async_client.post(PRODUCTS_URL, json={"name": "饼干", "category_ids": [c2_id]})

        response = await async_client.get(PRODUCTS_URL, params={"category_id": c1_id})
        data = response.json()["data"]
        assert data["total"] == 2


class TestGetProduct:
    @pytest.mark.smoke
    async def test_get_found(self, async_client: AsyncClient):
        created = await async_client.post(PRODUCTS_URL, json={"name": "商品X"})
        product_id = created.json()["data"]["id"]

        response = await async_client.get(f"{PRODUCTS_URL}/{product_id}")
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "商品X"


class TestUpdateProduct:
    async def test_update_success(self, async_client: AsyncClient):
        created = await async_client.post(PRODUCTS_URL, json={"name": "旧名称"})
        product_id = created.json()["data"]["id"]

        response = await async_client.put(
            f"{PRODUCTS_URL}/{product_id}", json={"name": "新名称"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "新名称"

    async def test_update_categories(self, async_client: AsyncClient):
        created = await async_client.post(PRODUCTS_URL, json={"name": "商品"})
        product_id = created.json()["data"]["id"]
        cat = await async_client.post("/api/categories", json={"name": "新分类"})
        cat_id = cat.json()["data"]["id"]

        response = await async_client.put(
            f"{PRODUCTS_URL}/{product_id}", json={"category_ids": [cat_id]}
        )
        assert response.status_code == 200


class TestDeleteProduct:
    async def test_delete_success(self, async_client: AsyncClient):
        created = await async_client.post(PRODUCTS_URL, json={"name": "待删除"})
        product_id = created.json()["data"]["id"]

        response = await async_client.delete(f"{PRODUCTS_URL}/{product_id}")
        assert response.status_code == 204
