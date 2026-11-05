"""业务逻辑层演示脚本，按教学顺序展示 service 层的核心用法。

运行方式：
    uv run --package web-service python apps/web-service/app/service/main.py
"""

import asyncio
from decimal import Decimal

from sqlalchemy import delete, text

from app.core.database import get_session_factory
from app.model.association import product_category
from app.model.category import Category
from app.model.product import Product
from app.model.sku import Sku
from app.schema.category import CategoryCreate
from app.schema.product import ProductCreate, ProductUpdate
from app.schema.sku import SkuCreate
from app.service.category_service import CategoryService
from app.service.product_service import ProductService
from app.service.sku_service import SkuService


async def main():
    async with get_session_factory()() as session:
        # ========== 0. 清理旧数据，保证幂等 ==========
        await session.execute(delete(Sku))
        await session.execute(delete(product_category))
        await session.execute(delete(Product))
        await session.execute(delete(Category))
        await session.execute(text("ALTER SEQUENCE sku_id_seq RESTART WITH 1"))
        await session.execute(text("ALTER SEQUENCE product_id_seq RESTART WITH 1"))
        await session.execute(text("ALTER SEQUENCE category_id_seq RESTART WITH 1"))
        await session.flush()

        # ========== 1. 创建分类 ==========
        print("========== 1. 创建分类 ==========")
        category_svc = CategoryService(session)
        c1 = await category_svc.create_category(
            CategoryCreate(name="电子产品", description="手机、电脑等")
        )
        c2 = await category_svc.create_category(CategoryCreate(name="图书"))
        c3 = await category_svc.create_category(CategoryCreate(name="服装"))
        print(
            f"创建分类: [{c1.id}] {c1.name}, [{c2.id}] {c2.name}, [{c3.id}] {c3.name}"
        )

        # ========== 2. 分页查询分类 ==========
        print("\n========== 2. 分页查询分类 ==========")
        result = await category_svc.list_categories(page=1, page_size=10)
        print(f"共 {result.total} 条, 当前页 {result.page}/{result.page_size} 条")
        for cat in result.items:
            print(f"  [{cat.id}] {cat.name}")

        # ========== 3. 创建商品并关联分类 ==========
        print("\n========== 3. 创建商品并关联分类 ==========")
        product_svc = ProductService(session)
        p1 = await product_svc.create_product(
            ProductCreate(
                name="iPhone 16",
                description="苹果最新款手机",
                brand="Apple",
                category_ids=[c1.id],
            )
        )
        p2 = await product_svc.create_product(
            ProductCreate(
                name="MacBook Pro",
                description="苹果笔记本电脑",
                brand="Apple",
                category_ids=[c1.id],
            )
        )
        p3 = await product_svc.create_product(
            ProductCreate(
                name="Python入门教程",
                description="零基础学Python",
                brand="人民邮电出版社",
                category_ids=[c2.id],
            )
        )
        print(
            f"创建商品: [{p1.id}] {p1.name}, [{p2.id}] {p2.name}, [{p3.id}] {p3.name}"
        )

        # ========== 4. 创建SKU ==========
        print("\n========== 4. 创建SKU ==========")
        sku_svc = SkuService(session)
        s1 = await sku_svc.create_sku(
            p1.id,
            SkuCreate(
                sku_code="IP16-128-BLK",
                price=Decimal("6999.00"),
                stock=100,
                attrs={"颜色": "黑色", "存储": "128G"},
                image_url="/images/ip16-blk.jpg",
            ),
        )
        assert s1 is not None
        s2 = await sku_svc.create_sku(
            p1.id,
            SkuCreate(
                sku_code="IP16-256-WHT",
                price=Decimal("7999.00"),
                stock=50,
                attrs={"颜色": "白色", "存储": "256G"},
                image_url="/images/ip16-wht.jpg",
            ),
        )
        assert s2 is not None
        s3 = await sku_svc.create_sku(
            p2.id,
            SkuCreate(
                sku_code="MBP14-M3-16G",
                price=Decimal("12999.00"),
                stock=30,
                attrs={"尺寸": "14寸", "芯片": "M3", "内存": "16G"},
                image_url="/images/mbp14.jpg",
            ),
        )
        assert s3 is not None
        print(
            f"创建SKU: [{s1.id}] {s1.sku_code} ¥{s1.price}, "
            f"[{s2.id}] {s2.sku_code} ¥{s2.price}, [{s3.id}] {s3.sku_code} ¥{s3.price}"
        )

        # ========== 5. 获取商品详情 ==========
        print("\n========== 5. 获取商品详情 ==========")
        detail = await product_svc.get_product(p1.id)
        assert detail is not None
        print(f"商品: {detail.name}")
        print(f"  分类: {[c.name for c in detail.categories]}")
        print(f"  SKU数: {len(detail.skus)}")
        for sku in detail.skus:
            print(f"    {sku.sku_code} | ¥{sku.price} | 库存:{sku.stock} | {sku.attrs}")

        # ========== 6. 按分类搜索商品 ==========
        print("\n========== 6. 按分类搜索商品 ==========")
        result = await product_svc.list_products(
            category_id=c1.id, page=1, page_size=10
        )
        print(f"「{c1.name}」分类下的商品共 {result.total} 件:")
        for p in result.items:
            print(f"  [{p.id}] {p.name} ({p.brand}) | {p.description[:20]}")

        # ========== 7. 按关键词搜索商品 ==========
        print("\n========== 7. 按关键词'Python'搜索商品 ==========")
        result = await product_svc.list_products(keyword="Python", page=1, page_size=10)
        print(f"匹配 'Python' 的商品共 {result.total} 件:")
        for p in result.items:
            print(f"  [{p.id}] {p.name}")

        # ========== 8. 更新SKU库存 ==========
        print("\n========== 8. 更新SKU库存 ==========")
        updated_sku = await sku_svc.update_stock(s1.id, 80)
        assert updated_sku is not None
        print(f"{s1.sku_code} 库存: {s1.stock} → {updated_sku.stock}")

        # ========== 9. 更新商品信息 ==========
        print("\n========== 9. 更新商品信息 ==========")
        updated = await product_svc.update_product(
            p2.id,
            ProductUpdate(
                description="2024款MacBook Pro M3芯片 笔记本电脑",
            ),
        )
        assert updated is not None
        print(f"更新后: {updated.name} → {updated.description}")

        # ========== 10. 获取分类详情（含商品列表） ==========
        print("\n========== 10. 获取分类详情 ==========")
        detail = await category_svc.get_category(c1.id)
        assert detail is not None
        print(f"分类「{detail.name}」下有 {len(detail.products)} 个商品:")
        for p in detail.products:
            print(f"  [{p.id}] {p.name}")

        await session.commit()
        print("\n========== 全部演示完毕 ==========")


if __name__ == "__main__":
    asyncio.run(main())
