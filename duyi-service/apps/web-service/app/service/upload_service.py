from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from duyi_utils.shared.file_util import get_suffix
from duyi_utils.shared.mime import IMAGE_MIME, get_mime_type
from duyi_utils.upload.aliyun import AliyunOSSConfig, AliyunOSSUploader

from app.exception.upload import UploadException
from app.model.setting import Setting
from app.model.setting_group import SettingGroup


class UploadService:

    def __init__(self, db: AsyncSession):
        self._db = db

    async def _get_oss_settings(self) -> dict[str, str]:
        result = await self._db.execute(
            select(SettingGroup)
            .options(selectinload(SettingGroup.settings))
            .where(SettingGroup.key == "aliyun_oss")
        )
        group = result.unique().scalar_one_or_none()
        if group is None:
            raise UploadException("OSS 上传配置未初始化")

        settings_map = {s.key: s.value for s in group.settings}
        required = {
            "oss_endpoint",
            "oss_access_key_id",
            "oss_access_key_secret",
            "oss_bucket_name",
        }
        for key in required:
            if not settings_map.get(key):
                raise UploadException(f"OSS 配置缺失: {key}")
        return settings_map

    async def generate_upload_sign(self, filename: str, file_size: int) -> dict:
        suffix = get_suffix(filename)
        if suffix is None:
            raise UploadException(f"无法获取文件后缀: {filename}")

        content_type = get_mime_type(suffix)
        if content_type is None:
            raise UploadException(f"不支持的文件类型: .{suffix}")

        if content_type not in IMAGE_MIME.values():
            raise UploadException(f"不支持的文件类型: {suffix}, 仅支持图片格式")

        oss_settings = await self._get_oss_settings()

        config = AliyunOSSConfig(
            access_key_id=oss_settings["oss_access_key_id"],
            access_key_secret=oss_settings["oss_access_key_secret"],
            bucket_name=oss_settings["oss_bucket_name"],
            endpoint=oss_settings["oss_endpoint"],
            mime_types=list(IMAGE_MIME.values()),
        )

        uploader = AliyunOSSUploader(config)
        credentials = uploader.generate_upload_credentials(filename, file_size)

        bucket_domain = oss_settings.get("oss_bucket_domain", "")
        if bucket_domain and not bucket_domain.startswith(("http://", "https://")):
            bucket_domain = f"//{bucket_domain}"

        credentials["bucket_domain"] = bucket_domain
        return credentials
