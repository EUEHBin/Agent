import inspect
from typing import Any

from fastapi import FastAPI

from app.core.middleware import response, process_time, cors, logging

MIDDLEWARES: list[tuple[Any, dict[str, Any]]] = [
    process_time.MIDDLEWARE,
    logging.MIDDLEWARE,
    cors.MIDDLEWARE,
    response.MIDDLEWARE,
]


def register_middleware(app: FastAPI) -> None:
    for callable_obj, kwargs in MIDDLEWARES:
        if inspect.isclass(callable_obj):
            app.add_middleware(callable_obj, **kwargs)  # type: ignore[arg-type]
        else:
            app.middleware("http")(callable_obj, **kwargs)  # type: ignore[type-var]
