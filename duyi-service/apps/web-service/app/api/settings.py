from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schema.setting import (
    SettingGroupResponse,
    SettingUpdateItem,
    SettingItemResponse,
)
from app.service.setting_service import SettingService

router = APIRouter(
    prefix="/api/settings",
    tags=["系统设置"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[SettingGroupResponse])
async def get_settings(db: Annotated[AsyncSession, Depends(get_db)]):
    return await SettingService(db).get_all()


@router.put("", response_model=list[SettingItemResponse])
async def update_settings(
    data: list[SettingUpdateItem],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await SettingService(db).update_settings(data)
