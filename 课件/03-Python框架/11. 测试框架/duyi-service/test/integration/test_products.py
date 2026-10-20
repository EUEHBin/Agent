import pytest
from httpx import AsyncClient


PRODUCTS_URL = "/api/products"


async def _create_product(client: AsyncClient, **kwargs) -> dict:
    defaults = {"name": "测试商品", "description": "这是一个测试商品", "brand": "测试品牌"}
    defaults.update(kwargs)
    response = await client.post(PRODUCTS_URL, json=defaults)
    assert response.status_code == 201
    return response.json()["data"]


class TestCreateProduct:
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
        response = await async_client.post(PRODUCTS_URL, json={
            "name": "商品B",
            "description": "描述B",
            "brand": "品牌B",
        })
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "商品B"
        assert data["description"] == "描述B"
        assert data["brand"] == "品牌B"

    async def test_create_with_categories(self, async_client: AsyncClient):
        category = await _create_category(async_client, name="分类1")

        response = await async_client.post(PRODUCTS_URL, json={
            "name": "商品C",
            "category_ids": [category["id"]],
        })
        assert response.status_code == 201
        data = response.json()["data"]
        assert len(data["categories"]) == 1
        assert data["categories"][0]["name"] == "分类1"

    async def test_create_missing_name(self, async_client: AsyncClient):
        response = await async_client.post(PRODUCTS_URL, json={})
        assert response.status_code == 422
        assert response.json()["data"]["code"] == "422001"

    async def test_create_with_nonexistent_category(self, async_client: AsyncClient):
        response = await async_client.post(PRODUCTS_URL, json={
            "name": "商品D",
            "category_ids": [99999],
        })
        assert response.status_code == 422
        assert response.json()["code"] == "422002"


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
        await _create_product(async_client, name="商品1")
        await _create_product(async_client, name="商品2")

        response = await async_client.get(PRODUCTS_URL)
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["items"]) == 2
        assert data["total"] == 2

    async def test_pagination(self, async_client: AsyncClient):
        for i in range(5):
            await _create_product(async_client, name=f"商品{i}")

        response = await async_client.get(PRODUCTS_URL, params={"page": 1, "page_size": 2})
        data = response.json()["data"]
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1

        response = await async_client.get(PRODUCTS_URL, params={"page": 2, "page_size": 2})
        data = response.json()["data"]
        assert len(data["items"]) == 2
        assert data["page"] == 2

        response = await async_client.get(PRODUCTS_URL, params={"page": 3, "page_size": 2})
        data = response.json()["data"]
        assert len(data["items"]) == 1

    async def test_filter_by_keyword(self, async_client: AsyncClient):
        await _create_product(async_client, name="苹果手机", description="高端智能手机")
        await _create_product(async_client, name="华为手机", description="国产旗舰")
        await _create_product(async_client, name="香蕉", description="水果")

        response = await async_client.get(PRODUCTS_URL, params={"keyword": "手机"})
        data = response.json()["data"]
        assert data["total"] == 2

    async def test_filter_by_brand(self, async_client: AsyncClient):
        await _create_product(async_client, name="产品A", brand="Apple")
        await _create_product(async_client, name="产品B", brand="华为")
        await _create_product(async_client, name="产品C", brand="Apple")

        response = await async_client.get(PRODUCTS_URL, params={"brand": "Apple"})
        data = response.json()["data"]
        assert data["total"] == 2

    async def test_filter_by_category(self, async_client: AsyncClient):
        c1 = await _create_category(async_client, name="电子")
        c2 = await _create_category(async_client, name="食品")

        await async_client.post(PRODUCTS_URL, json={
            "name": "笔记本", "category_ids": [c1["id"]],
        })
        await async_client.post(PRODUCTS_URL, json={
            "name": "手机", "category_ids": [c1["id"]],
        })
        await async_client.post(PRODUCTS_URL, json={
            "name": "饼干", "category_ids": [c2["id"]],
        })

        response = await async_client.get(PRODUCTS_URL, params={"category_id": c1["id"]})
        data = response.json()["data"]
        assert data["total"] == 2


class TestGetProduct:
    async def test_get_found(self, async_client: AsyncClient):
        product = await _create_product(async_client, name="商品X")

        response = await async_client.get(f"{PRODUCTS_URL}/{product['id']}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "商品X"

    async def test_get_not_found(self, async_client: AsyncClient):
        response = await async_client.get(f"{PRODUCTS_URL}/99999")
        assert response.status_code == 404
        assert response.json()["code"] == "404001"


class TestUpdateProduct:
    async def test_update_success(self, async_client: AsyncClient):
        product = await _create_product(async_client, name="旧名称")

        response = await async_client.put(
            f"{PRODUCTS_URL}/{product['id']}",
            json={"name": "新名称"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "新名称"

    async def test_update_categories(self, async_client: AsyncClient):
        product = await _create_product(async_client, name="商品")
        c1 = await _create_category(async_client, name="新分类")

        response = await async_client.put(
            f"{PRODUCTS_URL}/{product['id']}",
            json={"category_ids": [c1["id"]]},
        )
        assert response.status_code == 200

    async def test_update_not_found(self, async_client: AsyncClient):
        response = await async_client.put(f"{PRODUCTS_URL}/99999", json={"name": "x"})
        assert response.status_code == 404


class TestDeleteProduct:
    async def test_delete_success(self, async_client: AsyncClient, base_url: str):
        product = await _create_product(async_client, name="待删除")

        response = await async_client.delete(f"{PRODUCTS_URL}/{product['id']}")
        assert response.status_code == 204

        async with AsyncClient(base_url=base_url) as fresh_client:
            response = await fresh_client.get(f"{PRODUCTS_URL}/{product['id']}")
            assert response.status_code == 404

    async def test_delete_not_found(self, async_client: AsyncClient):
        response = await async_client.delete(f"{PRODUCTS_URL}/99999")
        assert response.status_code == 404


# ─── 辅助函数 ───

CATEGORIES_URL = "/api/categories"


async def _create_category(client: AsyncClient, name: str) -> dict:
    response = await client.post(CATEGORIES_URL, json={"name": name})
    assert response.status_code == 201
    return response.json()["data"]
