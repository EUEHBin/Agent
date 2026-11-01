from langgraph.config import get_config
from langgraph.runtime import get_runtime

from langgraph_python.states.core_agent_state import CoreAgentState


def _check_user_id():
    "检查是否有 user_id"
    config = get_config()
    metadata = config.get("metadata") or {}
    if "user_id" not in metadata or metadata["user_id"] is None:
        raise ValueError("Thread metadata 中缺少 user_id")


def _check_store():
    "检查是否有 store"
    runtime = get_runtime()
    if runtime.store is None:
        raise RuntimeError("长期记忆功能必须在提供 Store 的 Agent Server 中运行")


def check(state: CoreAgentState) -> dict:
    """检查图运行的必要信息"""
    _check_store()
    _check_user_id()
    return {}
