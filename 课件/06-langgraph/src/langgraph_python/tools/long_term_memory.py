from langchain.tools import ToolRuntime, tool

from langgraph_python.states.core_agent_state import ContextSchema, CoreAgentState


@tool
async def save_long_term_memory(
    memory: str,
    runtime: ToolRuntime[ContextSchema, CoreAgentState],
) -> str:
    """
    保存当前用户的一条长期记忆。

    当用户明确要求记住某件事，或者某项稳定信息对未来会话持续有用时使用。

    此操作会完全覆盖之前的记忆，如果要追加，请和之前的记忆合并后保存。
    """
    if runtime.store is None:
        raise RuntimeError("长期记忆工具必须在提供 Store 的 Agent Server 中运行")

    metadata = runtime.config.get("metadata") or {}
    if "user_id" not in metadata or metadata["user_id"] is None:
        raise ValueError("Thread metadata 中缺少 user_id")

    user_id = str(metadata["user_id"])
    await runtime.store.aput(
        ("users", user_id),
        key="memory",
        value={"content": memory},
    )
    return f"长期记忆已保存"
