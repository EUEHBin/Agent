from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any

from app.exception.base import BusinessException
from app.core.logger.log_record import LogRecord


@dataclass
class BusinessLog(LogRecord):
    action: str = ""
    entity: str = ""
    entity_id: str | int = ""


EntityIdExtractor = Callable[[tuple, dict[str, Any], Any], str | int]


def service_logger(
    action: str,
    entity: str = "",
    id_extractor: EntityIdExtractor | None = None,
):
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            log = BusinessLog(
                message="",
                action=action,
                entity=entity,
            )
            try:
                result = await func(*args, **kwargs)
                if id_extractor:
                    try:
                        log.entity_id = id_extractor(args, kwargs, result)
                    except Exception:
                        pass
                log.message = f"{action}成功"
                log.success()
                return result
            except Exception as e:
                if id_extractor:
                    try:
                        log.entity_id = id_extractor(args, kwargs, None)
                    except Exception:
                        pass
                log.message = f"{action}失败"
                if isinstance(e, BusinessException):
                    log.warning()
                else:
                    log.error(exc=e)
                raise

        return wrapper

    return decorator
