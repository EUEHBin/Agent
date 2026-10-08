from src.ai_tools import get_text

_WORKER_SYSTEM_PROMPT: str = """你是一个专业的调研助手。请根据分配的子任务进行调研，提供详细、准确的信息。输出应该是有条理的文本，便于后续汇总。"""


async def execute_subtask(index: int, total: int, subtask: str) -> str:
    print(f"   >> 任务 {index}/{total}: {subtask[:60]}{'...' if len(subtask) > 60 else ''}")

    messages: list[dict[str, str]] = [
        {"role": "system", "content": _WORKER_SYSTEM_PROMPT},
        {"role": "user", "content": f"请完成以下调研子任务：\n\n{subtask}"},
    ]
    result: str = await get_text(messages)

    print(f"   [完成] 任务 {index}/{total}")
    return result
