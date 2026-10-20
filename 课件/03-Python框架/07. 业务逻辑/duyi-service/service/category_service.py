from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.model.category import Category
from app.schema.category import (
    CategoryCreate,
    CategoryDetailResponse,
    CategoryResponse,
    CategoryUpdate,
)
from app.service.base import BaseService, PageResult


class CategoryService(BaseService):
    async def create_category(self, data: CategoryCreate) -> CategoryResponse:
        """创建分类"""
        category = Category(name=data.name, description=data.description)
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return CategoryResponse.model_validate(category)

    async def get_category(
        self, category_id: int
    ) -> CategoryDetailResponse | None:
        """根据ID获取分类详情，包含关联的商品列表"""
        stmt = (
            select(Category)
            .options(selectinload(Category.products))
            .where(Category.id == category_id)
        )
        result = await self.db.execute(stmt)
        category = result.unique().scalar_one_or_none()
        if category is None:
            return None
        return CategoryDetailResponse.model_validate(category)

    async def list_categories(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> PageResult[CategoryResponse]:
        """分页查询分类列表"""
        total = await self.db.scalar(select(func.count(Category.id)))

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Category)
            .offset(offset)
            .limit(page_size)
            .order_by(Category.id.asc())
        )
        items = [
            CategoryResponse.model_validate(c) for c in result.scalars().all()
        ]

        return PageResult(items=items, total=total or 0, page=page, page_size=page_size)

    async def update_category(
        self, category_id: int, data: CategoryUpdate
    ) -> CategoryResponse | None:
        """更新分类信息，仅更新传入的字段"""
        category = await self._get_category_orm(category_id)
        if category is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)

        await self.db.flush()
        await self.db.refresh(category)
        return CategoryResponse.model_validate(category)

    async def delete_category(self, category_id: int) -> bool:
        """删除分类"""
        category = await self._get_category_orm(category_id)
        if category is None:
            return False
        await self.db.delete(category)
        await self.db.flush()
        return True

    async def _get_category_orm(self, category_id: int) -> Category | None:
        """内部方法：获取 ORM 对象，用于更新/删除"""
        stmt = select(Category).where(Category.id == category_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
