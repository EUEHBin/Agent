import httpx
import pytest
from httpx import AsyncClient

REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
ME_URL = "/api/auth/me"
PASSWORD_URL = "/api/auth/password"


class TestRegister:
    @pytest.mark.smoke
    async def test_register_success(self, async_client: AsyncClient):
        response = await async_client.post(
            REGISTER_URL,
            json={"username": "e2ereguser", "password": "test123456"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["code"] == "0"
        assert body["data"]["username"] == "e2ereguser"
        assert "id" in body["data"]

    async def test_register_duplicate_fails(self, async_client: AsyncClient):
        await async_client.post(
            REGISTER_URL,
            json={"username": "dupuser", "password": "test123456"},
        )
        response = await async_client.post(
            REGISTER_URL,
            json={"username": "dupuser", "password": "test123456"},
        )
        assert response.status_code == 422
        assert "用户名已存在" in response.json()["message"]

    async def test_register_short_password_fails(self, async_client: AsyncClient):
        response = await async_client.post(
            REGISTER_URL,
            json={"username": "shortuser", "password": "12345"},
        )
        assert response.status_code == 422


class TestLogin:
    async def _register(self, async_client: AsyncClient) -> None:
        await async_client.post(
            REGISTER_URL,
            json={"username": "loginuser", "password": "test123456"},
        )

    @pytest.mark.smoke
    async def test_login_success(self, async_client: AsyncClient):
        await self._register(async_client)
        response = await async_client.post(
            LOGIN_URL,
            json={"username": "loginuser", "password": "test123456"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        assert body["data"]["access_token"]
        assert body["data"]["token_type"] == "bearer"

    async def test_login_wrong_password(self, async_client: AsyncClient):
        await self._register(async_client)
        response = await async_client.post(
            LOGIN_URL,
            json={"username": "loginuser", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "用户名或密码错误" in response.json()["message"]


class TestProfile:
    async def _get_token(self, async_client: AsyncClient) -> str:
        await async_client.post(
            REGISTER_URL,
            json={"username": "profileuser", "password": "test123456"},
        )
        resp = await async_client.post(
            LOGIN_URL,
            json={"username": "profileuser", "password": "test123456"},
        )
        return resp.json()["data"]["access_token"]

    @pytest.mark.smoke
    async def test_profile_requires_auth(self, async_client: AsyncClient):
        response = await async_client.get(ME_URL)
        assert response.status_code == 401

    async def test_profile_returns_user(self, async_client: AsyncClient):
        token = await self._get_token(async_client)
        response = await async_client.get(
            ME_URL, headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        assert body["data"]["username"] == "profileuser"


class TestChangePassword:
    async def _register_and_login(
        self, async_client: AsyncClient
    ) -> str:
        await async_client.post(
            REGISTER_URL,
            json={"username": "pwuser", "password": "old123456"},
        )
        resp = await async_client.post(
            LOGIN_URL,
            json={"username": "pwuser", "password": "old123456"},
        )
        return resp.json()["data"]["access_token"]

    @pytest.mark.smoke
    async def test_change_password_requires_auth(self, async_client: AsyncClient):
        response = await async_client.put(
            PASSWORD_URL,
            json={"old_password": "old", "new_password": "new123456"},
        )
        assert response.status_code == 401

    async def test_change_password_success(self, async_client: AsyncClient):
        token = await self._register_and_login(async_client)
        response = await async_client.put(
            PASSWORD_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={"old_password": "old123456", "new_password": "new123456"},
        )
        assert response.status_code == 204

        async with httpx.AsyncClient(base_url=str(async_client.base_url)) as client:
            login_resp = await client.post(
                LOGIN_URL,
                json={"username": "pwuser", "password": "new123456"},
            )
            assert login_resp.status_code == 200

    async def test_change_password_wrong_old(self, async_client: AsyncClient):
        token = await self._register_and_login(async_client)
        response = await async_client.put(
            PASSWORD_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={"old_password": "wrongold", "new_password": "new123456"},
        )
        assert response.status_code == 401
        assert "原密码错误" in response.json()["message"]
