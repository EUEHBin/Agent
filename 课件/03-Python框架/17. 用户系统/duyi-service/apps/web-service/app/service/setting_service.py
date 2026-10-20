from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.model.setting import Setting
from app.model.setting_group import SettingGroup
from app.schema.setting import (
    SettingGroupResponse,
    SettingUpdateItem,
    SettingItemResponse,
)
from app.service.base import BaseService


@dataclass(frozen=True)
class SettingDef:
    key: str
    value: str
    display_name: str
    description: str


@dataclass(frozen=True)
class SettingGroupDef:
    key: str
    display_name: str
    description: str
    settings: list[SettingDef]


SETTINGS_DTO: list[SettingGroupDef] = [
    SettingGroupDef(
        key="jwt",
        display_name="JWT配置",
        description="JWT令牌相关配置",
        settings=[
            SettingDef(
                key="jwt_expire_minutes",
                value="120",
                display_name="JWT过期时间",
                description="JWT令牌过期时间，单位为分钟，默认 120 分钟（2小时）",
            ),
        ],
    ),
    SettingGroupDef(
        key="aliyun_oss",
        display_name="阿里云OSS上传设置",
        description="阿里云OSS对象存储上传配置",
        settings=[
            SettingDef(
                key="oss_endpoint",
                value="",
                display_name="OSS Endpoint",
                description="例如 oss-cn-hangzhou.aliyuncs.com",
            ),
            SettingDef(
                key="oss_access_key_id",
                value="",
                display_name="AccessKey ID",
                description="RAM用户的AccessKey ID",
            ),
            SettingDef(
                key="oss_access_key_secret",
                value="",
                display_name="AccessKey Secret",
                description="RAM用户的AccessKey Secret",
            ),
            SettingDef(
                key="oss_bucket_name",
                value="",
                display_name="Bucket名称",
                description="OSS Bucket名称",
            ),
            SettingDef(
                key="oss_bucket_domain",
                value="",
                display_name="自定义域名",
                description="可选：自定义域名/CDN域名，留空则使用默认域名",
            ),
        ],
    ),
]


class SettingService(BaseService):

    async def initialize(self) -> dict[str, int]:
        dto_group_keys = {g.key for g in SETTINGS_DTO}

        result = await self.db.execute(
            select(SettingGroup).options(selectinload(SettingGroup.settings))
        )
        db_groups: dict[str, SettingGroup] = {
            g.key: g for g in result.unique().scalars().all()
        }

        groups_created = 0
        groups_deleted = 0
        settings_created = 0
        settings_deleted = 0

        for group_def in SETTINGS_DTO:
            db_group = db_groups.get(group_def.key)
            if db_group is None:
                db_group = SettingGroup(
                    key=group_def.key,
                    display_name=group_def.display_name,
                    description=group_def.description,
                )
                self.db.add(db_group)
                groups_created += 1
            else:
                db_group.display_name = group_def.display_name
                db_group.description = group_def.description

        await self.db.flush()

        for group_key in set(db_groups.keys()) - dto_group_keys:
            db_group = db_groups[group_key]
            for setting in db_group.settings:
                await self.db.delete(setting)
                settings_deleted += 1
            await self.db.delete(db_group)
            groups_deleted += 1

        await self.db.flush()

        for group_def in SETTINGS_DTO:
            db_group = db_groups.get(group_def.key)
            if db_group is None:
                db_group = (
                    (
                        await self.db.execute(
                            select(SettingGroup)
                            .options(selectinload(SettingGroup.settings))
                            .where(SettingGroup.key == group_def.key)
                        )
                    )
                    .unique()
                    .scalar_one()
                )

            dto_setting_keys = {s.key for s in group_def.settings}
            db_settings: dict[str, Setting] = {
                s.key: s
                for s in (db_group.settings if db_group.settings is not None else [])
            }

            for setting_def in group_def.settings:
                db_setting = db_settings.get(setting_def.key)
                if db_setting is None:
                    db_setting = Setting(
                        key=setting_def.key,
                        value=setting_def.value,
                        display_name=setting_def.display_name,
                        description=setting_def.description,
                        group_id=db_group.id,
                    )
                    self.db.add(db_setting)
                    settings_created += 1
                else:
                    db_setting.display_name = setting_def.display_name
                    db_setting.description = setting_def.description

            for setting_key in set(db_settings.keys()) - dto_setting_keys:
                await self.db.delete(db_settings[setting_key])
                settings_deleted += 1

        await self.db.flush()

        return {
            "groups_created": groups_created,
            "groups_deleted": groups_deleted,
            "settings_created": settings_created,
            "settings_deleted": settings_deleted,
        }

    async def get_all(self) -> list[SettingGroupResponse]:
        result = await self.db.execute(
            select(SettingGroup)
            .options(selectinload(SettingGroup.settings))
            .order_by(SettingGroup.id)
        )
        groups = result.unique().scalars().all()
        for g in groups:
            g.settings.sort(key=lambda s: s.id)
        return [SettingGroupResponse.model_validate(g) for g in groups]

    async def update_settings(
        self, data: list[SettingUpdateItem]
    ) -> list[SettingItemResponse]:
        update_map = {item.key: item.value for item in data}

        result = await self.db.execute(
            select(Setting).where(Setting.key.in_(update_map.keys()))
        )
        settings = result.unique().scalars().all()

        for setting in settings:
            setting.value = update_map[setting.key]

        await self.db.flush()
        return [SettingItemResponse.model_validate(s) for s in settings]
