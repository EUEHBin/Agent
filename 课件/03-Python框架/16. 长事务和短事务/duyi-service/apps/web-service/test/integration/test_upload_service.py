import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.upload import UploadException
from app.schema.setting import SettingUpdateItem
from app.service.setting_service import SettingService
from app.service.upload_service import UploadService


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


class TestGenerateUploadSign:
    async def _get_svc(self, db_session: AsyncSession) -> UploadService:
        await _init_oss_settings(db_session)
        return UploadService(db_session)

    @pytest.mark.smoke
    async def test_png_file_returns_credentials(
        self, db_session: AsyncSession
    ):
        svc = await self._get_svc(db_session)
        result = await svc.generate_upload_sign("photo.png", 1024)

        assert result["host"]
        assert result["access_id"]
        assert result["policy"]
        assert result["signature"]
        assert result["key"]
        assert result["content_type"] == "image/png"
        assert "bucket_domain" in result

    async def test_jpg_file_returns_credentials(
        self, db_session: AsyncSession
    ):
        svc = await self._get_svc(db_session)
        result = await svc.generate_upload_sign("photo.jpg", 2048)
        assert result["content_type"] == "image/jpeg"

    async def test_webp_file_returns_credentials(
        self, db_session: AsyncSession
    ):
        svc = await self._get_svc(db_session)
        result = await svc.generate_upload_sign("image.webp", 5120)
        assert result["content_type"] == "image/webp"

    async def test_bucket_domain_returned(self, db_session: AsyncSession):
        svc = await self._get_svc(db_session)
        result = await svc.generate_upload_sign("photo.png", 1024)
        assert "bucket_domain" in result

    async def test_key_starts_with_uploads(self, db_session: AsyncSession):
        svc = await self._get_svc(db_session)
        result = await svc.generate_upload_sign("photo.png", 1024)
        assert result["key"].startswith("uploads/")

    async def test_key_ends_with_correct_suffix(
        self, db_session: AsyncSession
    ):
        svc = await self._get_svc(db_session)
        result = await svc.generate_upload_sign("photo.png", 1024)
        assert result["key"].endswith(".png")


class TestGenerateUploadSignValidation:
    async def _get_svc(self, db_session: AsyncSession) -> UploadService:
        await _init_oss_settings(db_session)
        return UploadService(db_session)

    async def test_no_suffix_rejected(self, db_session: AsyncSession):
        svc = await self._get_svc(db_session)
        with pytest.raises(UploadException) as exc:
            await svc.generate_upload_sign("noextension", 1024)
        assert "无法获取文件后缀" in str(exc.value)

    async def test_pdf_rejected_not_image(self, db_session: AsyncSession):
        svc = await self._get_svc(db_session)
        with pytest.raises(UploadException) as exc:
            await svc.generate_upload_sign("doc.pdf", 1024)
        assert "仅支持图片格式" in str(exc.value)

    async def test_docx_rejected_not_image(self, db_session: AsyncSession):
        svc = await self._get_svc(db_session)
        with pytest.raises(UploadException) as exc:
            await svc.generate_upload_sign("report.docx", 1024)
        assert "仅支持图片格式" in str(exc.value)

    async def test_unknown_suffix_rejected(self, db_session: AsyncSession):
        svc = await self._get_svc(db_session)
        with pytest.raises(UploadException) as exc:
            await svc.generate_upload_sign("file.xyz", 1024)
        assert "不支持的文件类型" in str(exc.value)

    async def test_without_oss_settings_rejected(
        self, db_session: AsyncSession
    ):
        svc = UploadService(db_session)
        with pytest.raises(UploadException) as exc:
            await svc.generate_upload_sign("photo.png", 1024)
        assert "OSS 上传配置未初始化" in str(exc.value)
