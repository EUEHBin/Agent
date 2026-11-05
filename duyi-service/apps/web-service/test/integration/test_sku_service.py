from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.database import DatabaseException
from app.schema.product import ProductCreate
from app.schema.sku import SkuCreate, SkuUpdate
from app.service.product_service import ProductService
from app.service.sku_service import SkuService


def _sku_data(**kwargs):
    defaults = {
        "sku_code": "SKU-TEST-001",
        "price": Decimal("99.99"),
        "stock": 100,
        "attrs": {"color": "红色", "size": "L"},
        "image_url": "https://example.com/img.jpg",
    }
    defaults.update(kwargs)
    return SkuCreate(**defaults)


class TestCreateSku:
    @pytest.mark.smoke
    async def test_create_success(self, db_session: AsyncSession):
        product_svc = ProductService(db_session)
        product = await product_svc.create_product(ProductCreate(name="测试商品"))

        svc = SkuService(db_session)
        result = await svc.create_sku(product.id, _sku_data())
        assert result is not None
        assert result.sku_code == "SKU-TEST-001"
        assert result.price == Decimal("99.99")
        assert result.stock == 100
        assert result.attrs == {"color": "红色", "size": "L"}
        assert result.product_id == product.id

    async def test_create_product_not_found(self, db_session: AsyncSession):
        svc = SkuService(db_session)
        result = await svc.create_sku(99999, _sku_data())
        assert result is None

    async def test_create_duplicate_sku_code(self, db_session: AsyncSession):
        product_svc = ProductService(db_session)
        product = await product_svc.create_product(ProductCreate(name="商品"))

        svc = SkuService(db_session)
        await svc.create_sku(product.id, _sku_data(sku_code="DUP-CODE"))
        with pytest.raises(DatabaseException):
            await svc.create_sku(product.id, _sku_data(sku_code="DUP-CODE"))


class TestGetSku:
    async def test_get_found(self, db_session: AsyncSession):
        product_svc = ProductService(db_session)
        product = await product_svc.create_product(ProductCreate(name="商品"))
        sku_svc = SkuService(db_session)
        created = await sku_svc.create_sku(product.id, _sku_data(sku_code="GET-001"))

        result = await sku_svc.get_sku(created.id)
        assert result is not None
        assert result.sku_code == "GET-001"
        assert result.product_id == product.id

    async def test_get_not_found(self, db_session: AsyncSession):
        svc = SkuService(db_session)
        result = await svc.get_sku(99999)
        assert result is None


class TestListSkus:
    async def test_list_empty(self, db_session: AsyncSession):
        product_svc = ProductService(db_session)
        product = await product_svc.create_product(ProductCreate(name="无SKU商品"))

        svc = SkuService(db_session)
        result = await svc.list_skus(product.id)
        assert result == []

    async def test_list_with_data(self, db_session: AsyncSession):
        product_svc = ProductService(db_session)
        product = await product_svc.create_product(ProductCreate(name="有SKU商品"))

        svc = SkuService(db_session)
        await svc.create_sku(product.id, _sku_data(sku_code="A001"))
        await svc.create_sku(product.id, _sku_data(sku_code="A002"))

        result = await svc.list_skus(product.id)
        assert len(result) == 2


class TestUpdateSku:
    async def test_update_success(self, db_session: AsyncSession):
        product_svc = ProductService(db_session)
        product = await product_svc.create_product(ProductCreate(name="商品"))
        sku_svc = SkuService(db_session)
        created = await sku_svc.create_sku(
            product.id, _sku_data(sku_code="UPD-001", price=Decimal("10.00"))
        )

        result = await sku_svc.update_sku(
            created.id, SkuUpdate(price=Decimal("20.00"), stock=50)
        )
        assert result is not None
        assert result.price == Decimal("20.00")
        assert result.stock == 50
        assert result.sku_code == "UPD-001"

    async def test_update_not_found(self, db_session: AsyncSession):
        svc = SkuService(db_session)
        result = await svc.update_sku(99999, SkuUpdate(price=Decimal("1.00")))
        assert result is None


class TestDeleteSku:
    async def test_delete_success(self, db_session: AsyncSession):
        product_svc = ProductService(db_session)
        product = await product_svc.create_product(ProductCreate(name="商品"))
        sku_svc = SkuService(db_session)
        created = await sku_svc.create_sku(product.id, _sku_data(sku_code="DEL-001"))

        deleted = await sku_svc.delete_sku(created.id)
        assert deleted is True
        result = await sku_svc.get_sku(created.id)
        assert result is None

    async def test_delete_not_found(self, db_session: AsyncSession):
        svc = SkuService(db_session)
        deleted = await svc.delete_sku(99999)
        assert deleted is False


class TestUpdateStock:
    async def test_update_stock_success(self, db_session: AsyncSession):
        product_svc = ProductService(db_session)
        product = await product_svc.create_product(ProductCreate(name="商品"))
        sku_svc = SkuService(db_session)
        created = await sku_svc.create_sku(
            product.id, _sku_data(sku_code="STK-001", stock=10)
        )

        result = await sku_svc.update_stock(created.id, 200)
        assert result is not None
        assert result.stock == 200

    async def test_update_stock_not_found(self, db_session: AsyncSession):
        svc = SkuService(db_session)
        result = await svc.update_stock(99999, 100)
        assert result is None
