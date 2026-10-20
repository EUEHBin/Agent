import os

import pytest
from httpx import AsyncClient

UPLOAD_SIGN_URL = "/api/upload/sign"
SETTINGS_URL = "/api/settings"
REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"


def _oss_settings_payload() -> list[dict]:
    return [
        {"key": "oss_endpoint", "value": os.environ["OSS_ENDPOINT"]},
        {"key": "oss_access_key_id", "value": os.environ["OSS_ACCESS_KEY_ID"]},
        {
            "key": "oss_access_key_secret",
            "value": os.environ["OSS_ACCESS_KEY_SECRET"],
        },
        {"key": "oss_bucket_name", "value": os.environ["OSS_BUCKET_NAME"]},
        {
            "key": "oss_bucket_domain",
            "value": os.environ.get("OSS_BUCKET_DOMAIN", ""),
        },
    ]


async def _setup_oss_settings(client: AsyncClient, auth_headers: dict) -> None:
    await client.put(SETTINGS_URL, headers=auth_headers, json=_oss_settings_payload())


class TestUploadSign:
    @pytest.mark.smoke
    async def test_post_returns_credentials(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        await _setup_oss_settings(async_client, auth_headers)

        response = await async_client.post(
            UPLOAD_SIGN_URL,
            json={"filename": "photo.png", "file_size": 1024},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "0"
        data = body["data"]
        assert data["host"]
        assert data["access_id"]
        assert data["policy"]
        assert data["signature"]
        assert data["key"]
        assert data["content_type"] == "image/png"
        assert "bucket_domain" in data

    async def test_non_image_rejected(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        await _setup_oss_settings(async_client, auth_headers)

        response = await async_client.post(
            UPLOAD_SIGN_URL,
            json={"filename": "doc.pdf", "file_size": 1024},
        )
        assert response.status_code == 422
        assert "仅支持图片格式" in response.json()["message"]
