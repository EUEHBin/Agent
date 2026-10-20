import json
import re
from src.ai_tools import get_text

_DECOMPOSE_SYSTEM_PROMPT: str = """你是一个专业的任务分解专家。你的任务是将用户的调研需求分解成若干个相互独立的子任务。

要求：
1. 每个子任务应该聚焦于一个具体的方面
2. 子任务之间应该相互独立，没有依赖关系
3. 子任务数量控制在3-5个
4. 以JSON数组格式返回，每个元素是一个字符串描述

示例输出：
["子任务1的描述", "子任务2的描述", "子任务3的描述"]"""


def _parse_json_array(text: str) -> list[str]:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0]
    text = text.strip()

    try:
        result = json.loads(text)
        if isinstance(result, list):
            return [str(item) for item in result]
    except json.JSONDecodeError:
        pass

    match = re.search(r'\[[\s\S]*?\]', text)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list):
                return [str(item) for item in result]
        except json.JSONDecodeError:
            pass

    lines = [
        line.strip().strip("-").strip('"').strip("'").strip()
        for line in text.split("\n")
        if line.strip()
    ]
    return lines if lines else [text]


async def decompose(topic: str) -> list[str]:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": _DECOMPOSE_SYSTEM_PROMPT},
        {"role": "user", "content": f"调研需求：{topic}"},
    ]
    raw: str = await get_text(messages)
    return _parse_json_array(raw)
