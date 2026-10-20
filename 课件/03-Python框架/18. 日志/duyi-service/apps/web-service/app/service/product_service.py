from sqlalchemy import delete, exc as sa_exc, func, insert, select
from sqlalchemy.orm import selectinload

from app.model.association import product_category
from app.model.category import Category
from app.model.product import Product
from app.schema.product import (
    ProductBrief,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.service.base import BaseService, PageResult
from app.exception.database import DatabaseException
from app.core.logger import service_logger


class ProductService(BaseService):
    @service_logger(
        action="创建商品",
        entity="Product",
        id_extractor=lambda args, kwargs, result: str(result.id) if result else "",
    )
    async def create_product(self, data: ProductCreate) -> ProductResponse:
        """创建商品，同时建立与分类的关联"""
        product = Product(
            name=data.name,
            description=data.description,
            brand=data.brand,
        )
        self.db.add(product)
        await self.db.flush()

        if data.category_ids:
            try:
                await self.db.execute(
                    insert(product_category),
                    [
                        {"product_id": product.id, "category_id": cid}
                        for cid in data.category_ids
                    ],
                )
            except sa_exc.IntegrityError as e:
                raise DatabaseException(
                    message="关联的分类不存在",
                    detail=str(e),
                    original_exception=e,
                ) from e

        result = await self.get_product(product.id)
        assert result is not None
        return result

    async def get_product(self, product_id: int) -> ProductResponse | None:
        """根据ID获取商品详情，包含关联的分类列表和SKU列表"""
        stmt = (
            select(Product)
            .options(selectinload(Product.categories), selectinload(Product.skus))
            .where(Product.id == product_id)
        )
        result = await self.db.execute(stmt)
        product = result.unique().scalar_one_or_none()
        if product is None:
            return None
        return ProductResponse.model_validate(product)

    async def list_products(
        self,
        *,
        keyword: str | None = None,
        category_id: int | None = None,
        brand: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PageResult[ProductBrief]:
        """分页搜索商品列表，支持按关键词、分类、品牌筛选"""
        query = select(Product)

        if category_id is not None:
            query = query.join(Product.categories).where(Category.id == category_id)

        if keyword:
            query = query.where(
                Product.name.ilike(f"%{keyword}%")
                | Product.description.ilike(f"%{keyword}%")
            )

        if brand:
            query = query.where(Product.brand.ilike(f"%{brand}%"))

        total = await self.db.scalar(
            select(func.count()).select_from(query.subquery())
        )

        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.offset(offset).limit(page_size).order_by(Product.id.desc())
        )
        items = [
            ProductBrief.model_validate(p) for p in result.unique().scalars().all()
        ]

        return PageResult(items=items, total=total or 0, page=page, page_size=page_size)

    async def update_product(
        self, product_id: int, data: ProductUpdate
    ) -> ProductResponse | None:
        """更新商品信息，仅更新传入的字段"""
        product = await self._get_product_orm(product_id)
        if product is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        category_ids = update_data.pop("category_ids", None)

        for key, value in update_data.items():
            setattr(product, key, value)

        if category_ids is not None:
            await self.db.execute(
                delete(product_category).where(
                    product_category.c.product_id == product_id
                )
            )
            if category_ids:
                try:
                    await self.db.execute(
                        insert(product_category),
                        [
                            {"product_id": product_id, "category_id": cid}
                            for cid in category_ids
                        ],
                    )
                except sa_exc.IntegrityError as e:
                    raise DatabaseException(
                        message="关联的分类不存在",
                        detail=str(e),
                        original_exception=e,
                    ) from e

        await self.db.flush()
        # 重新加载，确保返回的 DTO 包含最新的关联数据
        return await self.get_product(product_id)

    @service_logger(
        action="删除商品",
        entity="Product",
        id_extractor=lambda args, kwargs, result: str(
            kwargs.get("product_id", args[0] if args else "")
        ),
    )
    async def delete_product(self, product_id: int) -> bool:
        """删除商品，关联的SKU会级联删除"""
        product = await self._get_product_orm(product_id)
        if product is None:
            return False
        await self.db.delete(product)
        await self.db.flush()
        return True

    async def _get_product_orm(self, product_id: int) -> Product | None:
        """内部方法：获取 ORM 对象，用于更新/删除"""
        stmt = (
            select(Product)
            .options(selectinload(Product.categories), selectinload(Product.skus))
            .where(Product.id == product_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()
