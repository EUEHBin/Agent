from ai_tools import completions

stream = completions([{"role": "user", "content": "你好"}])

for content in stream:
    print(content, end="", flush=True)
