from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from e2b import AsyncSandbox
import uuid
import json
from langchain_python.core.config import sandbox_settings


def _get_key(key: str | None) -> str:
    if key is None:
        key = str(uuid.uuid4())
    return key


def _get_store(store: BaseStore | None) -> BaseStore:
    if store is None:
        store = InMemoryStore()
    return store


def _get_metadata_config(key: str):
    return {
        "metadata": {
            "fc.sandbox.storage.oss": json.dumps(
                {
                    "mountPoints": [
                        {
                            "bucketName": sandbox_settings.oss_bucket,
                            "mountDir": "/home/user/skills",
                            "bucketPath": "/skills",
                            "endpoint": sandbox_settings.oss_endpoint,
                            "readOnly": False,
                        },
                        {
                            "bucketName": sandbox_settings.oss_bucket,
                            "mountDir": "/home/user/workspace",
                            "bucketPath": f"/{key}/workspace",
                            "endpoint": sandbox_settings.oss_endpoint,
                            "readOnly": False,
                        },
                        {
                            "bucketName": sandbox_settings.oss_bucket,
                            "mountDir": "/home/user/output",
                            "bucketPath": f"/{key}/output",
                            "endpoint": sandbox_settings.oss_endpoint,
                            "readOnly": False,
                        },
                    ]
                }
            ),
            "fc.sandbox.auth.role": sandbox_settings.role_arn,
        }
    }


TIMEOUT = 300
basic_config = {
    "timeout": TIMEOUT,  # 从创建开始计时，时间到了自动销毁
    "api_key": sandbox_settings.api_key,
    "api_url": sandbox_settings.api_url,
    "domain": sandbox_settings.domain,
}

_STORE_NAMESPACE = ("project",)


async def _get_sandbox_id(store: BaseStore, key: str) -> str | None:
    item = await store.aget(_STORE_NAMESPACE, key)
    if not item:
        return None
    if not item.value:
        return None
    return item.value.get("sandbox_id", None)


async def get_sandbox(
    *, key: str | None = None, store: BaseStore | None = None
) -> AsyncSandbox:
    "获取一个沙箱"
    key = _get_key(key)
    store = _get_store(store)
    # 获取挂载点的config
    metadata_config = _get_metadata_config(key)

    # 获取sandbox_id
    sandbox_id = await _get_sandbox_id(store, key)
    if sandbox_id is not None:
        # 连接沙箱
        try:
            sandbox = await AsyncSandbox.connect(sandbox_id=sandbox_id, **basic_config)
            await sandbox.set_timeout(TIMEOUT)
            return sandbox
        except:
            pass

    # 创建沙箱
    sandbox = await AsyncSandbox.create(
        template=sandbox_settings.template,
        **basic_config,  # type: ignore
        **metadata_config,
    )

    await store.aput(_STORE_NAMESPACE, key, {"sandbox_id": sandbox.sandbox_id})
    return sandbox
