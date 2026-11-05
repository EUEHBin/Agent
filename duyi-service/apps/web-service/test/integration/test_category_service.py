from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.category import CategoryCreate, CategoryUpdate
from app.service.category_service import CategoryService


class TestCreateCategory:
    @pytest.mark.smoke
    async def test_create_with_all_fields(self, db_session: AsyncSession):
        svc = CategoryService(db_session)
        result = await svc.create_category(CategoryCreate(name="电子产品", description="电子数码产品"))
        assert result.id is not None
        assert result.name == "电子产品"
        assert result.description == "电子数码产品"

    async def test_create_with_default_description(self, db_session: AsyncSession):
        svc = CategoryService(db_session)
        result = await svc.create_category(CategoryCreate(name="图书"))
        assert result.name == "图书"
        assert result.description == ""


class TestGetCategory:
    async def test_get_found(self, db_session: AsyncSession):
        svc = CategoryService(db_session)
        created = await svc.create_category(CategoryCreate(name="服装"))
        result = await svc.get_category(created.id)
        assert result is not None
        assert result.name == "服装"
        assert result.products == []

    async def test_get_not_found(self, db_session: AsyncSession):
        svc = CategoryService(db_session)
        result = await svc.get_category(99999)
        assert result is None


class TestListCategories:
    async def test_list_empty(self, db_session: AsyncSession):
        svc = CategoryService(db_session)
        result = await svc.list_categories()
        assert result.items == []
        assert result.total == 0
        assert result.page == 1
        assert result.page_size == 20

    async def test_list_with_data(self, db_session: AsyncSession):
        svc = CategoryService(db_session)
        await svc.create_category(CategoryCreate(name="A"))
        await svc.create_category(CategoryCreate(name="B"))
        result = await svc.list_categories()
        assert len(result.items) == 2
        assert result.total == 2

    async def test_pagination(self, db_session: AsyncSession):
        svc = CategoryService(db_session)
        for i in range(5):
            await svc.create_category(CategoryCreate(name=f"分类{i}"))

        page1 = await svc.list_categories(page=1, page_size=2)
        assert len(page1.items) == 2
        assert page1.total == 5

        page3 = await svc.list_categories(page=3, page_size=2)
        assert len(page3.items) == 1


class TestUpdateCategory:
    async def test_update_success(self, db_session: AsyncSession):
        svc = CategoryService(db_session)
        created = await svc.create_category(CategoryCreate(name="旧名称"))
        result = await svc.update_category(created.id, CategoryUpdate(name="新名称"))
        assert result is not None
        assert result.name == "新名称"

    async def test_update_not_found(self, db_session: AsyncSession):
        svc = CategoryService(db_session)
        result = await svc.update_category(99999, CategoryUpdate(name="x"))
        assert result is None


class TestDeleteCategory:
    async def test_delete_success(self, db_session: AsyncSession):
        svc = CategoryService(db_session)
        created = await svc.create_category(CategoryCreate(name="待删除"))
        deleted = await svc.delete_category(created.id)
        assert deleted is True
        result = await svc.get_category(created.id)
        assert result is None

    async def test_delete_not_found(self, db_session: AsyncSession):
        svc = CategoryService(db_session)
        deleted = await svc.delete_category(99999)
        assert deleted is False
