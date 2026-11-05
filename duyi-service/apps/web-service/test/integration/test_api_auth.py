import pytest
from httpx import AsyncClient

from app.exception.auth import AuthException
from app.exception.base import BusinessException

AUTH_REGISTER_URL = "/api/auth/register"
AUTH_LOGIN_URL = "/api/auth/login"
AUTH_ME_URL = "/api/auth/me"
AUTH_PASSWORD_URL = "/api/auth/password"


class TestRegister:
    @pytest.mark.smoke
    async def test_register_success(self, async_client: AsyncClient):
        response = await async_client.post(
            AUTH_REGISTER_URL,
            json={"username": "newuser", "password": "test123456"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["code"] == "0"
        assert body["data"]["username"] == "newuser"
        assert "id" in body["data"]

    async def test_register_duplicate_username(self, async_client: AsyncClient):
        await async_client.post(
            AUTH_REGISTER_URL,
            json={"username": "dupuser", "password": "test123456"},
        )
        with pytest.raises(BusinessException, match="用户名已存在"):
            await async_client.post(
                AUTH_REGISTER_URL,
                json={"username": "dupuser", "password": "test123456"},
            )

    async def test_register_short_password(self, async_client: AsyncClient):
        response = await async_client.post(
            AUTH_REGISTER_URL,
            json={"username": "shortpw", "password": "12345"},
        )
        assert response.status_code == 422

    async def test_register_empty_username(self, async_client: AsyncClient):
        response = await async_client.post(
            AUTH_REGISTER_URL,
            json={"username": "", "password": "test123456"},
        )
        assert response.status_code == 422


class TestLogin:
    @pytest.mark.smoke
    async def test_login_success(self, async_client: AsyncClient):
        await async_client.post(
            AUTH_REGISTER_URL,
            json={"username": "loginuser", "password": "test123456"},
        )

        response = await async_client.post(
            AUTH_LOGIN_URL,
            json={"username": "loginuser", "password": "test123456"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        assert body["data"]["access_token"]
        assert body["data"]["token_type"] == "bearer"

    async def test_login_wrong_password(self, async_client: AsyncClient):
        await async_client.post(
            AUTH_REGISTER_URL,
            json={"username": "wrongpwuser", "password": "test123456"},
        )

        with pytest.raises(AuthException, match="用户名或密码错误"):
            await async_client.post(
                AUTH_LOGIN_URL,
                json={"username": "wrongpwuser", "password": "wrongpassword"},
            )

    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        with pytest.raises(AuthException, match="用户名或密码错误"):
            await async_client.post(
                AUTH_LOGIN_URL,
                json={"username": "nouser", "password": "test123456"},
            )


class TestProfile:
    async def _login(self, async_client: AsyncClient) -> str:
        await async_client.post(
            AUTH_REGISTER_URL,
            json={"username": "profileuser", "password": "test123456"},
        )
        resp = await async_client.post(
            AUTH_LOGIN_URL,
            json={"username": "profileuser", "password": "test123456"},
        )
        return resp.json()["data"]["access_token"]

    @pytest.mark.smoke
    async def test_profile_requires_auth(self, async_client: AsyncClient):
        response = await async_client.get(AUTH_ME_URL)
        assert response.status_code == 401

    async def test_profile_success(self, async_client: AsyncClient):
        token = await self._login(async_client)

        response = await async_client.get(
            AUTH_ME_URL,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        assert body["data"]["username"] == "profileuser"


class TestChangePassword:
    async def _login(
        self, async_client: AsyncClient, username: str, password: str
    ) -> str:
        resp = await async_client.post(
            AUTH_LOGIN_URL,
            json={"username": username, "password": password},
        )
        return resp.json()["data"]["access_token"]

    @pytest.mark.smoke
    async def test_change_password_requires_auth(self, async_client: AsyncClient):
        response = await async_client.put(
            AUTH_PASSWORD_URL,
            json={"old_password": "old", "new_password": "new123456"},
        )
        assert response.status_code == 401

    async def test_change_password_success(self, async_client: AsyncClient):
        await async_client.post(
            AUTH_REGISTER_URL,
            json={"username": "pwuser", "password": "old123456"},
        )
        token = await self._login(async_client, "pwuser", "old123456")

        response = await async_client.put(
            AUTH_PASSWORD_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={"old_password": "old123456", "new_password": "new123456"},
        )
        assert response.status_code == 204

        login_resp = await async_client.post(
            AUTH_LOGIN_URL,
            json={"username": "pwuser", "password": "new123456"},
        )
        assert login_resp.status_code == 200

    async def test_change_password_wrong_old(self, async_client: AsyncClient):
        await async_client.post(
            AUTH_REGISTER_URL,
            json={"username": "pwuser2", "password": "old123456"},
        )
        token = await self._login(async_client, "pwuser2", "old123456")

        with pytest.raises(AuthException, match="原密码错误"):
            await async_client.put(
                AUTH_PASSWORD_URL,
                headers={"Authorization": f"Bearer {token}"},
                json={"old_password": "wrongold", "new_password": "new123456"},
            )
