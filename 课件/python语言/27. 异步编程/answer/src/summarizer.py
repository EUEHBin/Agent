from src.ai_tools import get_text

_SUMMARIZER_SYSTEM_PROMPT: str = """你是一个专业的报告撰写专家。请将以下多个独立的调研结果整合成一份结构清晰、内容完整的调研报告。

报告要求：
1. 需要有标题和概述
2. 每个部分需要逻辑连贯
3. 总结关键发现
4. 使用Markdown格式"""


async def summarize(topic: str, merged: str) -> str:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": _SUMMARIZER_SYSTEM_PROMPT},
        {"role": "user", "content": f"以下是关于「{topic}」的多个子任务调研结果，请整合成一份完整的调研报告：\n\n{merged}"},
    ]
    return await get_text(messages)
