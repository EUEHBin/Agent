from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from langchain.chat_models import init_chat_model
from langchain.tools import ToolRuntime, tool
from langgraph.store.base import BaseStore
from langchain_python.core.config import anthropic_settings
from typing import Any
from langgraph.runtime import Runtime


@tool
async def write_store_item(key: str, value: str, runtime: ToolRuntime) -> str:
    """写入一条数据到持久化的存储。

    Args:
        key: 键
        value: 值
    """

    if runtime.store is None:
        raise RuntimeError("该工具无法找到存储")
    assert runtime.server_info is not None
    assert runtime.server_info.user is not None
    await runtime.store.aput(
        (runtime.server_info.user.identity, "store-demo", "tool"),
        key,
        {
            "value": value,
        },
    )
    return "数据已写入"


model = init_chat_model(
    model=anthropic_settings.default_model,
    model_provider="anthropic",
    thinking={"type": "disabled"},
)


system_prompt = """
你是一个用于验证 Store 授权 namespace 前缀重写的测试 Agent。
每次收到用户消息后，必须严格按照下列顺序执行：

1. 调用 write_store_item，key 使用 "latest"，value 使用用户消息原文。
2. 调用 write_file，file_path 使用 "/backend-proof.txt"，content 使用用户消息原文。
3. 两个工具都成功后，简短告知用户写入完成。

不要自己向 namespace 添加用户 ID。
"""


def get_backend_namespace(rt: Runtime[Any]) -> tuple[str, ...]:
    assert rt.server_info is not None
    assert rt.server_info.user is not None

    return (
        rt.server_info.user.identity,
        "store-demo",
        "backend",
    )


agent = create_deep_agent(
    model=model,
    tools=[write_store_item],
    system_prompt=system_prompt,
    backend=StoreBackend(namespace=get_backend_namespace),
)
