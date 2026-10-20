import sys
import json
from typing import AsyncGenerator
import httpx
from src.config import API_BASE, MODEL_NAME, API_KEY

_URL: str = f"{API_BASE.rstrip('/')}/chat/completions"

if not API_KEY:
    print("错误: 请在 .env 文件中配置 API_KEY")
    sys.exit(1)


async def completions(messages: list[dict[str, str]]) -> AsyncGenerator[str, None]:
    headers: dict[str, str] = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": True,
    }
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", _URL, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue


async def get_text(messages: list[dict[str, str]]) -> str:
    result: list[str] = []
    async for chunk in completions(messages):
        result.append(chunk)
    return "".join(result)
