from langgraph.config import get_config
from langgraph.runtime import Runtime

from langgraph_python.states.core_agent_state import ContextSchema, CoreAgentState
from langchain_core.utils.mustache import render

SYSTEM_PROMPT_TEMPLATE = """
# 管理员指令

以下内容来自管理员注入的提示词

```text
{{assistant_system_prompt}}
```

# 用户长期记忆

长期记忆用于保存跨会话仍然有价值的用户信息，例如用户明确要求记住的事情、稳定的偏好和持续有用的背景信息。

在处理长期记忆时，请遵守以下规则：
- 当用户明确要求你记住某件事时，调用长期记忆工具保存它。
- 当信息是稳定的用户偏好、身份背景或未来会话可能反复用到的信息时，可以调用长期记忆工具保存它。
- 不要保存只对当前任务有用的临时信息，也不要保存根据对话推测出的不确定信息。
- 每个用户只保存一条键名为 `memory` 的长期记忆数据。保存新内容会完全覆盖旧内容；如果需要追加信息，请先将新旧内容合并后再保存。
- 你无须关心用户id，系统会自行追踪不同身份的用户

以下内容是当前用户的长期记忆：

```
{{long_term_memory}}
```
"""


async def initialize_system_prompt(
    state: CoreAgentState,
    runtime: Runtime[ContextSchema],
) -> dict:
    """首次运行时生成系统提示词快照，后续运行保持不变。"""
    if state.get("system_prompt") is not None:
        return {}

    assistant_system_prompt = ""  # assistant中的系统提示词
    long_term_memory = ""  # 长期记忆
    # 处理系统提示词
    if runtime.context and runtime.context.system_prompt:
        assistant_system_prompt = runtime.context.system_prompt

    # 处理长期记忆
    if runtime.store is not None:
        metadata = get_config().get("metadata") or {}
        user_id = str(metadata["user_id"])
        memory = await runtime.store.aget(("users", user_id), key="memory")
        if memory:
            long_term_memory = memory.value.get("content", "")

    system_prompt = render(
        SYSTEM_PROMPT_TEMPLATE,
        {
            "assistant_system_prompt": assistant_system_prompt,
            "long_term_memory": long_term_memory,
        },
    )
    return {"system_prompt": system_prompt}
