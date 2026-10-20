from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.database import DatabaseException
from app.schema.category import CategoryCreate
from app.schema.product import ProductCreate, ProductUpdate
from app.service.category_service import CategoryService
from app.service.product_service import ProductService


class TestCreateProduct:
    @pytest.mark.smoke
    async def test_create_with_required_fields(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        result = await svc.create_product(ProductCreate(name="商品A"))
        assert result.id is not None
        assert result.name == "商品A"
        assert result.description == ""
        assert result.brand is None
        assert result.categories == []
        assert result.skus == []

    async def test_create_with_all_fields(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        result = await svc.create_product(
            ProductCreate(name="商品B", description="描述B", brand="品牌B")
        )
        assert result.name == "商品B"
        assert result.description == "描述B"
        assert result.brand == "品牌B"

    async def test_create_with_categories(self, db_session: AsyncSession):
        cat_svc = CategoryService(db_session)
        cat = await cat_svc.create_category(CategoryCreate(name="分类1"))

        svc = ProductService(db_session)
        result = await svc.create_product(
            ProductCreate(name="商品C", category_ids=[cat.id])
        )
        assert len(result.categories) == 1
        assert result.categories[0].name == "分类1"

    async def test_create_with_nonexistent_category(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        with pytest.raises(DatabaseException):
            await svc.create_product(ProductCreate(name="商品D", category_ids=[99999]))


class TestGetProduct:
    async def test_get_found(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        created = await svc.create_product(ProductCreate(name="商品X"))
        result = await svc.get_product(created.id)
        assert result is not None
        assert result.name == "商品X"

    async def test_get_not_found(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        result = await svc.get_product(99999)
        assert result is None


class TestListProducts:
    async def test_list_empty(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        result = await svc.list_products()
        assert result.items == []
        assert result.total == 0
        assert result.page == 1

    async def test_list_with_data(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        await svc.create_product(ProductCreate(name="商品1"))
        await svc.create_product(ProductCreate(name="商品2"))
        result = await svc.list_products()
        assert len(result.items) == 2
        assert result.total == 2

    async def test_pagination(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        for i in range(5):
            await svc.create_product(ProductCreate(name=f"商品{i}"))

        page1 = await svc.list_products(page=1, page_size=2)
        assert len(page1.items) == 2
        assert page1.total == 5
        assert page1.page == 1

        page2 = await svc.list_products(page=2, page_size=2)
        assert len(page2.items) == 2
        assert page2.page == 2

        page3 = await svc.list_products(page=3, page_size=2)
        assert len(page3.items) == 1

    async def test_filter_by_keyword(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        await svc.create_product(ProductCreate(name="苹果手机", description="高端智能手机"))
        await svc.create_product(ProductCreate(name="华为手机", description="国产旗舰"))
        await svc.create_product(ProductCreate(name="香蕉", description="水果"))

        result = await svc.list_products(keyword="手机")
        assert result.total == 2

    async def test_filter_by_brand(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        await svc.create_product(ProductCreate(name="产品A", brand="Apple"))
        await svc.create_product(ProductCreate(name="产品B", brand="华为"))
        await svc.create_product(ProductCreate(name="产品C", brand="Apple"))

        result = await svc.list_products(brand="Apple")
        assert result.total == 2

    async def test_filter_by_category(self, db_session: AsyncSession):
        cat_svc = CategoryService(db_session)
        c1 = await cat_svc.create_category(CategoryCreate(name="电子"))
        c2 = await cat_svc.create_category(CategoryCreate(name="食品"))

        svc = ProductService(db_session)
        await svc.create_product(ProductCreate(name="笔记本", category_ids=[c1.id]))
        await svc.create_product(ProductCreate(name="手机", category_ids=[c1.id]))
        await svc.create_product(ProductCreate(name="饼干", category_ids=[c2.id]))

        result = await svc.list_products(category_id=c1.id)
        assert result.total == 2


class TestUpdateProduct:
    async def test_update_success(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        created = await svc.create_product(ProductCreate(name="旧名称"))
        result = await svc.update_product(created.id, ProductUpdate(name="新名称"))
        assert result is not None
        assert result.name == "新名称"

    async def test_update_categories(self, db_session: AsyncSession):
        cat_svc = CategoryService(db_session)
        cat = await cat_svc.create_category(CategoryCreate(name="新分类"))

        svc = ProductService(db_session)
        created = await svc.create_product(ProductCreate(name="商品"))
        result = await svc.update_product(created.id, ProductUpdate(category_ids=[cat.id]))
        assert result is not None
        assert result.id == created.id

    async def test_update_clear_categories(self, db_session: AsyncSession):
        cat_svc = CategoryService(db_session)
        cat = await cat_svc.create_category(CategoryCreate(name="分类"))

        svc = ProductService(db_session)
        created = await svc.create_product(ProductCreate(name="商品", category_ids=[cat.id]))
        result = await svc.update_product(created.id, ProductUpdate(category_ids=[]))
        assert result is not None
        assert result.id == created.id

    async def test_update_not_found(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        result = await svc.update_product(99999, ProductUpdate(name="x"))
        assert result is None


class TestDeleteProduct:
    async def test_delete_success(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        created = await svc.create_product(ProductCreate(name="待删除"))
        deleted = await svc.delete_product(created.id)
        assert deleted is True
        result = await svc.get_product(created.id)
        assert result is None

    async def test_delete_not_found(self, db_session: AsyncSession):
        svc = ProductService(db_session)
        deleted = await svc.delete_product(99999)
        assert deleted is False
