import asyncio
import base64
import hashlib
import hmac
import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable

import oss2

from duyi_utils.shared.file_util import get_suffix
from duyi_utils.shared.mime import get_mime_type
from duyi_utils.upload.dir_strategy import date_uuid_strategy


@dataclass
class AliyunOSSConfig:
    """阿里云 OSS 上传配置"""

    access_key_id: str
    access_key_secret: str
    bucket_name: str
    endpoint: str
    dir_strategy: Callable[[], str] = field(default=date_uuid_strategy)
    expire_seconds: int = 3600
    mime_types: list[str] | None = None


class AliyunOSSUploader:
    """阿里云 OSS 上传器，提供上传凭证生成、删除、存在性判断功能。"""

    def __init__(self, config: AliyunOSSConfig):
        self._config = config
        self._host = f"https://{config.bucket_name}.{config.endpoint}"

        auth = oss2.Auth(config.access_key_id, config.access_key_secret)
        self._bucket = oss2.Bucket(auth, config.endpoint, config.bucket_name)

    def generate_upload_credentials(self, filename: str, file_size: int) -> dict:
        """
        生成阿里云 OSS PostObject 上传凭证。

        Args:
            filename: 文件路径，如 "/a/b/c/1.txt"，仅取最后的文件名。
            file_size: 文件大小，单位字节。

        Returns:
            上传凭证字典：
                - host: OSS Bucket 域名，表单 POST 的目标地址
                - access_id: OSSAccessKeyId，表单字段
                - policy: Base64 编码的策略文档，表单字段
                - signature: 策略的 HMAC-SHA1 签名，表单字段
                - key: 最终的文件在 OSS 中的路径
                - content_type: 文件的 MIME 类型

        Raises:
            ValueError: 无法获取文件后缀，或文件类型不被支持。
        """
        basename = os.path.basename(filename)
        suffix = get_suffix(basename)
        if suffix is None:
            raise ValueError(f"无法获取文件后缀: {basename}")

        content_type = get_mime_type(suffix)
        if content_type is None:
            raise ValueError(f"不支持的文件类型: .{suffix}")

        if self._config.mime_types and content_type not in self._config.mime_types:
            raise ValueError(f"不允许上传的类型: {content_type}")

        dir_ = self._config.dir_strategy()
        key = f"{dir_}{uuid.uuid4().hex}.{suffix}"

        expire_time = datetime.now(timezone.utc) + timedelta(
            seconds=self._config.expire_seconds
        )
        expiration = expire_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        policy_dict = {
            "expiration": expiration,
            "conditions": [
                ["eq", "$key", key],
                ["eq", "$Content-Type", content_type],
                ["content-length-range", 0, file_size],
            ],
        }

        policy_json = json.dumps(policy_dict)
        policy = base64.b64encode(policy_json.encode()).decode()

        signature = base64.b64encode(
            hmac.new(
                self._config.access_key_secret.encode(),
                policy.encode(),
                hashlib.sha1,
            ).digest()
        ).decode()

        return {
            "host": self._host,
            "access_id": self._config.access_key_id,
            "policy": policy,
            "signature": signature,
            "key": key,
            "content_type": content_type,
        }

    async def delete(self, object_key: str) -> None:
        """
        删除 OSS 中指定 key 的文件。

        Args:
            object_key: OSS 中文件的 key。

        Raises:
            oss2.exceptions.OssError: 删除失败时抛出。
        """
        await asyncio.to_thread(self._bucket.delete_object, object_key)

    async def exists(self, object_key: str) -> bool:
        """
        判断 OSS 中指定 key 的文件是否存在。

        Args:
            object_key: OSS 中文件的 key。

        Returns:
            True 表示文件存在，False 表示不存在。
        """
        return await asyncio.to_thread(self._bucket.object_exists, object_key)
