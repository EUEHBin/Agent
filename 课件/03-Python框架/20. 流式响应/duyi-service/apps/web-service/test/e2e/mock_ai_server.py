"""Mock AI server —— 模拟 OpenAI 兼容的 chat/completions 流式接口，供 e2e 测试使用。"""
import json
import sys

from starlette.applications import Starlette
from starlette.responses import Response, StreamingResponse
from starlette.routing import Route

MOCK_RESPONSE = "Mock AI回应内容，用于测试验证。"


async def _chat_completions(request):
    async def stream():
        for i, char in enumerate(MOCK_RESPONSE):
            chunk = {
                "id": f"mock-{i}",
                "object": "chat.completion.chunk",
                "choices": [{"delta": {"content": char}, "index": 0}],
            }
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


async def _health(request):
    return Response(b"ok", status_code=200, media_type="text/plain")


routes = [
    Route("/chat/completions", _chat_completions, methods=["POST"]),
    Route("/health", _health, methods=["GET"]),
]

app = Starlette(routes=routes)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 18001
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
