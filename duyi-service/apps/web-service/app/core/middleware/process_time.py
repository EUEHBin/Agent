import time
from typing import Any

from fastapi import Request


async def process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round((time.perf_counter() - start) * 1000, 2))
    return response


MIDDLEWARE: tuple[Any, dict[str, Any]] = (process_time, {})
