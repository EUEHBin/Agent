from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


@dataclass
class PageResult(Generic[T]):
    """分页结果"""
    items: list[T]
    total: int
    page: int
    page_size: int


class BaseService:
    """业务逻辑基类，所有 Service 继承此类，共享 session"""

    def __init__(self, db: AsyncSession):
        self.db = db
