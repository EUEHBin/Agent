import base64
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from duyi_utils.upload.aliyun import AliyunOSSConfig, AliyunOSSUploader


@pytest.fixture
def config():
    return AliyunOSSConfig(
        access_key_id="test-access-key-id",
        access_key_secret="test-access-key-secret",
        bucket_name="test-bucket",
        endpoint="oss-cn-hangzhou.aliyuncs.com",
        mime_types=["image/png", "application/pdf"],
    )


@pytest.fixture
def uploader(config):
    with patch("duyi_utils.upload.aliyun.oss2.Auth") as mock_auth, \
         patch("duyi_utils.upload.aliyun.oss2.Bucket") as mock_bucket:
        uploader = AliyunOSSUploader(config)
        uploader._bucket = mock_bucket.return_value
        yield uploader


class TestGenerateUploadCredentials:
    def test_successful_credential_generation(self, config):
        with patch("duyi_utils.upload.aliyun.oss2.Auth"), \
             patch("duyi_utils.upload.aliyun.oss2.Bucket"), \
             patch("duyi_utils.upload.aliyun.uuid.uuid4") as mock_uuid, \
             patch("duyi_utils.upload.aliyun.datetime") as mock_dt, \
             patch("duyi_utils.upload.dir_strategy.datetime") as mock_dir_dt:
            mock_uuid.return_value.hex = "a1b2c3d4e5f6"
            mock_dt.now.return_value = datetime(2025, 6, 26, 10, 0, 0, tzinfo=timezone.utc)
            mock_dir_dt.now.return_value = datetime(2025, 6, 26, 10, 0, 0)

            uploader = AliyunOSSUploader(config)
            result = uploader.generate_upload_credentials("photo.png", 102400)

        assert result["host"] == "https://test-bucket.oss-cn-hangzhou.aliyuncs.com"
        assert result["access_id"] == "test-access-key-id"
        assert result["content_type"] == "image/png"
        assert result["key"] == "uploads/2025/06/26/a1b2c3d4e5f6.png"
        assert result["policy"] is not None
        assert result["signature"] is not None

    def test_policy_contains_exact_key_match(self, config):
        with patch("duyi_utils.upload.aliyun.oss2.Auth"), \
             patch("duyi_utils.upload.aliyun.oss2.Bucket"), \
             patch("duyi_utils.upload.aliyun.uuid.uuid4") as mock_uuid, \
             patch("duyi_utils.upload.aliyun.datetime") as mock_dt:
            mock_uuid.return_value.hex = "a1b2c3d4e5f6"
            mock_dt.now.return_value = datetime(2025, 6, 26, 10, 0, 0, tzinfo=timezone.utc)

            uploader = AliyunOSSUploader(config)
            result = uploader.generate_upload_credentials("photo.png", 102400)

        policy_json = base64.b64decode(result["policy"]).decode()
        policy_dict = json.loads(policy_json)
        conditions = policy_dict["conditions"]

        assert ["eq", "$key", result["key"]] in conditions
        assert ["eq", "$Content-Type", "image/png"] in conditions
        assert ["content-length-range", 0, 102400] in conditions

    def test_default_expire_one_hour(self, config):
        with patch("duyi_utils.upload.aliyun.oss2.Auth"), \
             patch("duyi_utils.upload.aliyun.oss2.Bucket"), \
             patch("duyi_utils.upload.aliyun.uuid.uuid4") as mock_uuid, \
             patch("duyi_utils.upload.aliyun.datetime") as mock_dt:
            mock_uuid.return_value.hex = "a1b2c3d4e5f6"
            mock_dt.now.return_value = datetime(2025, 6, 26, 10, 0, 0, tzinfo=timezone.utc)

            uploader = AliyunOSSUploader(config)
            result = uploader.generate_upload_credentials("photo.png", 102400)

        policy_json = base64.b64decode(result["policy"]).decode()
        policy_dict = json.loads(policy_json)

        assert policy_dict["expiration"] == "2025-06-26T11:00:00.000Z"

    def test_raises_on_missing_suffix(self, config):
        with patch("duyi_utils.upload.aliyun.oss2.Auth"), \
             patch("duyi_utils.upload.aliyun.oss2.Bucket"):
            uploader = AliyunOSSUploader(config)
            with pytest.raises(ValueError, match="无法获取文件后缀"):
                uploader.generate_upload_credentials("noext", 1024)

    def test_raises_on_unsupported_type(self, config):
        with patch("duyi_utils.upload.aliyun.oss2.Auth"), \
             patch("duyi_utils.upload.aliyun.oss2.Bucket"):
            uploader = AliyunOSSUploader(config)
            with pytest.raises(ValueError, match="不支持的文件类型"):
                uploader.generate_upload_credentials("file.xyz", 1024)

    def test_raises_on_not_allowed_mime_type(self, config):
        config.mime_types = ["application/pdf"]
        with patch("duyi_utils.upload.aliyun.oss2.Auth"), \
             patch("duyi_utils.upload.aliyun.oss2.Bucket"):
            uploader = AliyunOSSUploader(config)
            with pytest.raises(ValueError, match="不允许上传的类型"):
                uploader.generate_upload_credentials("photo.png", 1024)

    def test_path_filename_extracts_basename(self, config):
        with patch("duyi_utils.upload.aliyun.oss2.Auth"), \
             patch("duyi_utils.upload.aliyun.oss2.Bucket"), \
             patch("duyi_utils.upload.aliyun.uuid.uuid4") as mock_uuid, \
             patch("duyi_utils.upload.aliyun.datetime") as mock_dt:
            mock_uuid.return_value.hex = "a1b2c3d4e5f6"
            mock_dt.now.return_value = datetime(2025, 6, 26, 10, 0, 0, tzinfo=timezone.utc)

            uploader = AliyunOSSUploader(config)
            result = uploader.generate_upload_credentials("/a/b/c/report.pdf", 1024)

        assert result["content_type"] == "application/pdf"
        assert result["key"].endswith(".pdf")

    def test_doc_file_type(self, config):
        with patch("duyi_utils.upload.aliyun.oss2.Auth"), \
             patch("duyi_utils.upload.aliyun.oss2.Bucket"), \
             patch("duyi_utils.upload.aliyun.uuid.uuid4") as mock_uuid, \
             patch("duyi_utils.upload.aliyun.datetime") as mock_dt:
            mock_uuid.return_value.hex = "a1b2c3d4e5f6"
            mock_dt.now.return_value = datetime(2025, 6, 26, 10, 0, 0, tzinfo=timezone.utc)

            uploader = AliyunOSSUploader(config)
            result = uploader.generate_upload_credentials("doc.pdf", 2048)

        assert result["content_type"] == "application/pdf"


class TestDelete:
    async def test_delete_calls_bucket_delete_object(self, uploader):
        with patch("duyi_utils.upload.aliyun.asyncio.to_thread") as mock_to_thread:
            await uploader.delete("uploads/2025/06/26/test.png")
            mock_to_thread.assert_called_once_with(
                uploader._bucket.delete_object, "uploads/2025/06/26/test.png"
            )


class TestExists:
    async def test_exists_true(self, uploader):
        with patch("duyi_utils.upload.aliyun.asyncio.to_thread", return_value=True):
            result = await uploader.exists("uploads/2025/06/26/test.png")
            assert result is True

    async def test_exists_false(self, uploader):
        with patch("duyi_utils.upload.aliyun.asyncio.to_thread", return_value=False):
            result = await uploader.exists("uploads/2025/06/26/test.png")
            assert result is False
