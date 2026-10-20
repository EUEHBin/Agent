"""集成测试：使用真实的阿里云 OSS 环境进行测试。

要求：
  1. 在项目根目录提供 .env.test 文件，包含 OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET / OSS_ENDPOINT / OSS_BUCKET_NAME。
  2. 该 Bucket 需要有读写权限。
"""

import base64
import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timezone

import pytest
from dotenv import load_dotenv

from duyi_utils.upload.aliyun import AliyunOSSConfig, AliyunOSSUploader


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".env.test"))


@pytest.fixture(scope="module")
def config():
    return AliyunOSSConfig(
        access_key_id=os.environ["OSS_ACCESS_KEY_ID"],
        access_key_secret=os.environ["OSS_ACCESS_KEY_SECRET"],
        bucket_name=os.environ["OSS_BUCKET_NAME"],
        endpoint=os.environ["OSS_ENDPOINT"],
        mime_types=["image/png", "image/jpeg", "application/pdf"],
    )


@pytest.fixture(scope="module")
def uploader(config):
    return AliyunOSSUploader(config)


class TestGenerateUploadCredentialsIntegration:
    def test_returns_required_fields(self, uploader):
        result = uploader.generate_upload_credentials("photo.png", 1024)
        for field in ("host", "access_id", "policy", "signature", "key", "content_type"):
            assert field in result
            assert result[field]

    def test_host_matches_bucket_and_endpoint(self, uploader, config):
        result = uploader.generate_upload_credentials("photo.png", 1024)
        assert result["host"] == f"https://{config.bucket_name}.{config.endpoint}"

    def test_key_starts_with_uploads(self, uploader):
        result = uploader.generate_upload_credentials("photo.png", 1024)
        assert result["key"].startswith("uploads/")

    def test_key_ends_with_correct_suffix(self, uploader):
        result = uploader.generate_upload_credentials("photo.png", 1024)
        assert result["key"].endswith(".png")

    def test_content_type_matches_file_suffix(self, uploader):
        result = uploader.generate_upload_credentials("photo.png", 1024)
        assert result["content_type"] == "image/png"

        result = uploader.generate_upload_credentials("report.pdf", 2048)
        assert result["content_type"] == "application/pdf"

    def test_policy_can_be_decoded(self, uploader):
        result = uploader.generate_upload_credentials("photo.png", 1024)
        policy_json = base64.b64decode(result["policy"]).decode()
        policy_dict = json.loads(policy_json)

        assert "expiration" in policy_dict
        assert "conditions" in policy_dict
        conditions = policy_dict["conditions"]

        assert ["eq", "$key", result["key"]] in conditions
        assert ["eq", "$Content-Type", "image/png"] in conditions
        assert ["content-length-range", 0, 1024] in conditions

    def test_signature_verifiable(self, uploader, config):
        result = uploader.generate_upload_credentials("photo.png", 1024)
        expected_signature = base64.b64encode(
            hmac.new(
                config.access_key_secret.encode(),
                result["policy"].encode(),
                hashlib.sha1,
            ).digest()
        ).decode()

        assert result["signature"] == expected_signature

    def test_expiration_is_near_one_hour_later(self, uploader):
        result = uploader.generate_upload_credentials("photo.png", 1024)
        policy_json = base64.b64decode(result["policy"]).decode()
        policy_dict = json.loads(policy_json)

        expire_str = policy_dict["expiration"]
        expire_time = datetime.strptime(expire_str, "%Y-%m-%dT%H:%M:%S.000Z").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = expire_time - now
        assert 3500 < delta.total_seconds() < 3700  # 约 1 小时


def _build_multipart_body(cred, filename, content, key=None, content_type=None):
    """拼装 OSS PostObject 的 multipart/form-data 请求体"""
    boundary = "----TestBoundary"
    body_parts = [
        f"--{boundary}",
        f'Content-Disposition: form-data; name="OSSAccessKeyId"',
        "",
        cred["access_id"],
        f"--{boundary}",
        f'Content-Disposition: form-data; name="policy"',
        "",
        cred["policy"],
        f"--{boundary}",
        f'Content-Disposition: form-data; name="signature"',
        "",
        cred["signature"],
        f"--{boundary}",
        f'Content-Disposition: form-data; name="key"',
        "",
        key if key is not None else cred["key"],
        f"--{boundary}",
        f'Content-Disposition: form-data; name="Content-Type"',
        "",
        content_type if content_type is not None else cred["content_type"],
        f"--{boundary}",
        f'Content-Disposition: form-data; name="success_action_status"',
        "",
        "200",
        f"--{boundary}",
        f'Content-Disposition: form-data; name="file"; filename="{filename}"',
        f"Content-Type: {content_type if content_type is not None else cred['content_type']}",
        "",
        content,
        f"--{boundary}--",
    ]
    body = "\r\n".join(body_parts).encode()
    return body, boundary


def _do_upload(cred, body, boundary):
    """执行 OSS PostObject 上传请求，返回响应"""
    import urllib.request

    req = urllib.request.Request(
        cred["host"],
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    return urllib.request.urlopen(req)


class TestUploadAndDelete:
    async def test_upload_delete_and_exists_flow(self, uploader):
        """完整流程测试：
        1. 生成上传凭证
        2. 上传一个测试文件到 OSS
        3. 检查文件存在
        4. 删除文件
        5. 确认文件不存在
        """
        cred = uploader.generate_upload_credentials("test.png", 1024)
        body, boundary = _build_multipart_body(cred, "test.png", "fake-image-content")

        response = _do_upload(cred, body, boundary)
        assert response.status == 200

        assert await uploader.exists(cred["key"]) is True

        await uploader.delete(cred["key"])

        assert await uploader.exists(cred["key"]) is False

    def test_upload_with_wrong_key_rejected(self, uploader):
        """验证：获得签名后更换 Key 上传会被 OSS 拒绝"""
        import urllib.error

        cred = uploader.generate_upload_credentials("test.png", 1024)
        wrong_key = cred["key"].replace("uploads/", "uploads_fake/")
        body, boundary = _build_multipart_body(cred, "test.png", "fake-image-content", key=wrong_key)

        with pytest.raises(urllib.error.HTTPError) as exc_info:
            _do_upload(cred, body, boundary)
        assert exc_info.value.code in (400, 403)

    def test_upload_with_wrong_content_type_rejected(self, uploader):
        """验证：获得签名后更换 Content-Type 上传会被 OSS 拒绝"""
        import urllib.error

        cred = uploader.generate_upload_credentials("test.png", 1024)
        wrong_content_type = "image/jpeg"
        body, boundary = _build_multipart_body(
            cred, "test.png", "fake-image-content", content_type=wrong_content_type
        )

        with pytest.raises(urllib.error.HTTPError) as exc_info:
            _do_upload(cred, body, boundary)
        assert exc_info.value.code in (400, 403)

    def test_upload_with_exceeded_file_size_rejected(self, uploader):
        """验证：上传文件大小超过签名中指定的大小会被 OSS 拒绝"""
        import urllib.error

        cred = uploader.generate_upload_credentials("test.png", 1024)
        large_content = "x" * 2048
        body, boundary = _build_multipart_body(cred, "test.png", large_content)

        with pytest.raises(urllib.error.HTTPError) as exc_info:
            _do_upload(cred, body, boundary)
        assert exc_info.value.code in (400, 403)
