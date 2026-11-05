"""FastAPI 全局异常处理器"""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.exception.base import BusinessException
from app.exception.handler.errors import ERROR_MAP, PROTOCOL_ERROR_MAP


def _lookup(exc: Exception) -> tuple[str, int, str]:
    """按 MRO 查找异常对应的错误码配置，找不到则回退到 Exception"""
    for exc_type in type(exc).__mro__:
        if exc_type in ERROR_MAP:
            return ERROR_MAP[exc_type]
    return ERROR_MAP[Exception]


def _format_validation_error(err: dict) -> str:
    loc = ".".join(str(p) for p in err["loc"])
    return f"{loc}: {err['msg']}"


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request.state.exception_handled = True
    if isinstance(exc, HTTPException):
        code = str(exc.status_code)
        http_status = exc.status_code
        body_msg = PROTOCOL_ERROR_MAP.get(exc.status_code, exc.detail)
    else:
        code, http_status, default_msg = _lookup(exc)

        if isinstance(exc, RequestValidationError):
            messages = [_format_validation_error(e) for e in exc.errors()]
            body_msg = "\n".join(messages)
        elif isinstance(exc, BusinessException):
            body_msg = exc.message
        else:
            body_msg = default_msg

    # 日志记录
    log = request.state.request_log
    if log:
        log.message = f"请求异常: {body_msg}"
        if http_status == 500:
            log.error(exc=exc)
        else:
            log.warning()

    return JSONResponse(
        status_code=http_status,
        content={"code": code, "message": body_msg, "data": None},
    )
