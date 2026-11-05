import os

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.setting import SettingUpdateItem
from app.service.setting_service import SettingService

UPLOAD_SIGN_URL = "/api/upload/sign"


def _oss_settings_from_env() -> list[SettingUpdateItem]:
    return [
        SettingUpdateItem(key="oss_endpoint", value=os.environ["OSS_ENDPOINT"]),
        SettingUpdateItem(
            key="oss_access_key_id", value=os.environ["OSS_ACCESS_KEY_ID"]
        ),
        SettingUpdateItem(
            key="oss_access_key_secret", value=os.environ["OSS_ACCESS_KEY_SECRET"]
        ),
        SettingUpdateItem(
            key="oss_bucket_name", value=os.environ["OSS_BUCKET_NAME"]
        ),
        SettingUpdateItem(
            key="oss_bucket_domain", value=os.environ.get("OSS_BUCKET_DOMAIN", "")
        ),
    ]


async def _init_oss_settings(db_session: AsyncSession):
    svc = SettingService(db_session)
    await svc.initialize()
    await svc.update_settings(_oss_settings_from_env())


class TestGetUploadSign:
    @pytest.mark.smoke
    async def test_post_returns_credentials(
        self, db_session: AsyncSession, async_client: AsyncClient
    ):
        await _init_oss_settings(db_session)

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

    async def test_jpg_returns_jpeg_content_type(
        self, db_session: AsyncSession, async_client: AsyncClient
    ):
        await _init_oss_settings(db_session)

        response = await async_client.post(
            UPLOAD_SIGN_URL,
            json={"filename": "photo.jpg", "file_size": 2048},
        )
        assert response.status_code == 200
        assert response.json()["data"]["content_type"] == "image/jpeg"

    async def test_webp_returns_credentials(
        self, db_session: AsyncSession, async_client: AsyncClient
    ):
        await _init_oss_settings(db_session)

        response = await async_client.post(
            UPLOAD_SIGN_URL,
            json={"filename": "image.webp", "file_size": 5120},
        )
        assert response.status_code == 200
        assert response.json()["data"]["content_type"] == "image/webp"

    async def test_bucket_domain_in_response(
        self, db_session: AsyncSession, async_client: AsyncClient
    ):
        await _init_oss_settings(db_session)

        response = await async_client.post(
            UPLOAD_SIGN_URL,
            json={"filename": "photo.png", "file_size": 1024},
        )
        assert response.status_code == 200
        assert "bucket_domain" in response.json()["data"]

    async def test_empty_filename_rejected(
        self, db_session: AsyncSession, async_client: AsyncClient
    ):
        await _init_oss_settings(db_session)

        response = await async_client.post(
            UPLOAD_SIGN_URL,
            json={"filename": "", "file_size": 1024},
        )
        assert response.status_code == 422

    async def test_zero_file_size_rejected(
        self, db_session: AsyncSession, async_client: AsyncClient
    ):
        await _init_oss_settings(db_session)

        response = await async_client.post(
            UPLOAD_SIGN_URL,
            json={"filename": "photo.png", "file_size": 0},
        )
        assert response.status_code == 422
