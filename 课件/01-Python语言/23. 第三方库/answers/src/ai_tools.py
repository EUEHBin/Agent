import sys
import os
import json
from typing import Generator
import requests
from dotenv import load_dotenv

load_dotenv()
_API_BASE: str = os.getenv("API_BASE", "https://api.openai.com/v1")
_MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
_API_KEY: str = os.getenv("API_KEY", "")
_URL: str = f"{_API_BASE.rstrip('/')}/chat/completions"

if not _API_KEY:
    print("错误: 请在 .env 文件中配置 API_KEY")
    sys.exit(1)


def completions(messages: list[dict[str, str]]) -> Generator[str, None, None]:
    headers: dict[str, str] = {
        "Authorization": f"Bearer {_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _MODEL_NAME,
        "messages": messages,
        "stream": True,
    }
    resp = requests.post(_URL, headers=headers, json=payload, stream=True)
    resp.raise_for_status()

    for line in resp.iter_lines():
        if not line:
            continue
        text: str = line.decode("utf-8")
        if not text.startswith("data: "):
            continue
        data_str = text[6:]
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
