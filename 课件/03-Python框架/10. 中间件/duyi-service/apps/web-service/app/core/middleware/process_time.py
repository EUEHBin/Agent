import time

from fastapi import Request


async def process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(time.perf_counter() - start, 4))
    return response


MIDDLEWARE = (process_time, {})
