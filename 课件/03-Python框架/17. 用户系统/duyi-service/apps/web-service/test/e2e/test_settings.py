import pytest
from httpx import AsyncClient

SETTINGS_URL = "/api/settings"


class TestGetSettings:
    @pytest.mark.smoke
    async def test_requires_auth(self, async_client: AsyncClient):
        response = await async_client.get(SETTINGS_URL)
        assert response.status_code == 401

    @pytest.mark.smoke
    async def test_get_returns_ok(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        response = await async_client.get(SETTINGS_URL, headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        assert isinstance(body["data"], list)


class TestUpdateSettings:
    @pytest.mark.smoke
    async def test_requires_auth(self, async_client: AsyncClient):
        response = await async_client.put(
            SETTINGS_URL,
            json=[{"key": "oss_endpoint", "value": "test"}],
        )
        assert response.status_code == 401

    @pytest.mark.smoke
    async def test_put_returns_ok(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        response = await async_client.put(
            SETTINGS_URL,
            headers=auth_headers,
            json=[{"key": "oss_endpoint", "value": "test"}],
        )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        assert isinstance(body["data"], list)
