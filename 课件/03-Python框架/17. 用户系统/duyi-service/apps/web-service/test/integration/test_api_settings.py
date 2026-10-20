import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.setting_service import SettingService, SETTINGS_DTO

SETTINGS_URL = "/api/settings"


class TestGetSettings:
    @pytest.mark.smoke
    async def test_requires_auth(self, async_client: AsyncClient):
        response = await async_client.get(SETTINGS_URL)
        assert response.status_code == 401

    async def test_empty_before_initialize(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        response = await async_client.get(SETTINGS_URL, headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        assert body["data"] == []

    async def test_returns_data_after_initialize(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        await SettingService(db_session).initialize()

        response = await async_client.get(SETTINGS_URL, headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        data = body["data"]
        assert len(data) == len(SETTINGS_DTO)
        assert data[0]["key"] == SETTINGS_DTO[0].key
        assert len(data[0]["settings"]) == len(SETTINGS_DTO[0].settings)


class TestUpdateSettings:
    @pytest.mark.smoke
    async def test_requires_auth(self, async_client: AsyncClient):
        response = await async_client.put(
            SETTINGS_URL,
            json=[{"key": "oss_endpoint", "value": "test"}],
        )
        assert response.status_code == 401

    async def test_update_single_key(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        await SettingService(db_session).initialize()

        response = await async_client.put(
            SETTINGS_URL,
            headers=auth_headers,
            json=[{"key": "oss_endpoint", "value": "https://new.example.com"}],
        )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        assert len(body["data"]) == 1
        assert body["data"][0]["key"] == "oss_endpoint"
        assert body["data"][0]["value"] == "https://new.example.com"

    async def test_update_multiple_keys(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        await SettingService(db_session).initialize()

        response = await async_client.put(
            SETTINGS_URL,
            headers=auth_headers,
            json=[
                {"key": "oss_endpoint", "value": "v1"},
                {"key": "oss_bucket_name", "value": "my-bucket"},
            ],
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

    async def test_update_without_initialize_returns_empty(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        response = await async_client.put(
            SETTINGS_URL,
            headers=auth_headers,
            json=[{"key": "oss_endpoint", "value": "x"}],
        )
        assert response.status_code == 200
        assert response.json()["data"] == []
