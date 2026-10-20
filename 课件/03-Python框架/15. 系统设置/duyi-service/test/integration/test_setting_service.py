import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.setting import SettingUpdateItem
from app.service.setting_service import SettingService, SETTINGS_DTO


class TestInitialize:
    @pytest.mark.smoke
    async def test_first_initialize_creates_data(self, db_session: AsyncSession):
        svc = SettingService(db_session)
        result = await svc.initialize()

        assert result["groups_created"] == len(SETTINGS_DTO)
        expected_settings_count = sum(len(g.settings) for g in SETTINGS_DTO)
        assert result["settings_created"] == expected_settings_count
        assert result["groups_deleted"] == 0
        assert result["settings_deleted"] == 0

    async def test_reinitialize_is_idempotent(self, db_session: AsyncSession):
        svc = SettingService(db_session)
        await svc.initialize()
        result = await svc.initialize()

        assert result["groups_created"] == 0
        assert result["settings_created"] == 0
        assert result["groups_deleted"] == 0
        assert result["settings_deleted"] == 0


class TestGetAll:
    async def test_empty_before_initialize(self, db_session: AsyncSession):
        svc = SettingService(db_session)
        result = await svc.get_all()
        assert result == []

    async def test_returns_groups_after_initialize(self, db_session: AsyncSession):
        svc = SettingService(db_session)
        await svc.initialize()
        result = await svc.get_all()

        assert len(result) == len(SETTINGS_DTO)
        group = result[0]
        assert group.key == SETTINGS_DTO[0].key
        assert group.display_name == SETTINGS_DTO[0].display_name
        assert len(group.settings) == len(SETTINGS_DTO[0].settings)


class TestUpdateSettings:
    async def _init_and_get_svc(self, db_session: AsyncSession) -> SettingService:
        svc = SettingService(db_session)
        await svc.initialize()
        return svc

    @pytest.mark.smoke
    async def test_update_single_key(self, db_session: AsyncSession):
        svc = await self._init_and_get_svc(db_session)

        result = await svc.update_settings(
            [SettingUpdateItem(key="oss_endpoint", value="https://new.example.com")]
        )
        assert len(result) == 1
        assert result[0].key == "oss_endpoint"
        assert result[0].value == "https://new.example.com"

    async def test_update_multiple_keys(self, db_session: AsyncSession):
        svc = await self._init_and_get_svc(db_session)

        result = await svc.update_settings(
            [
                SettingUpdateItem(key="oss_endpoint", value="v1"),
                SettingUpdateItem(key="oss_bucket_name", value="my-bucket"),
            ]
        )
        assert len(result) == 2
        values = {r.key: r.value for r in result}
        assert values["oss_endpoint"] == "v1"
        assert values["oss_bucket_name"] == "my-bucket"

    async def test_update_no_matching_key_returns_empty(self, db_session: AsyncSession):
        svc = await self._init_and_get_svc(db_session)

        result = await svc.update_settings(
            [SettingUpdateItem(key="nonexistent_key", value="x")]
        )
        assert result == []

    async def test_update_empty_value(self, db_session: AsyncSession):
        svc = await self._init_and_get_svc(db_session)

        result = await svc.update_settings(
            [SettingUpdateItem(key="oss_endpoint", value="")]
        )
        assert len(result) == 1
        assert result[0].value == ""
