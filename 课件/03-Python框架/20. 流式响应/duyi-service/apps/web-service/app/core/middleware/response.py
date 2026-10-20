import json
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

_NO_BODY_STATUS = frozenset(range(100, 200)) | {204, 304}


async def unified_response(request: Request, call_next):
    response = await call_next(request)

    if (
        not request.url.path.startswith("/api/")
        or getattr(request.state, "exception_handled", False)
        or getattr(request.state, "is_stream", False)
        or request.method == "HEAD"
        or response.status_code in _NO_BODY_STATUS
    ):
        return response

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    headers = dict(response.headers)
    headers.pop("content-length", None)

    data = json.loads(body) if body else None

    return JSONResponse(
        content={"code": "0", "data": data, "message": "success"},
        status_code=response.status_code,
        headers=headers,
    )


MIDDLEWARE: tuple[Any, dict[str, Any]] = (unified_response, {})
