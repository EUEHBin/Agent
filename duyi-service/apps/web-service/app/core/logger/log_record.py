import contextvars
import sys
import time
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path

from loguru import logger

from app.core.config import common_settings, log_settings


class LogLevel(StrEnum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "_request_id", default=""
)


def setup_logging() -> None:
    logger.remove()
    if common_settings.environment == "production":
        logger.add(
            sys.stdout,
            level=log_settings.level,
            serialize=True,
        )
    else:
        logger.add(
            sys.stdout,
            level=log_settings.level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{extra[request_id]}</cyan> | "
                "<yellow>{extra[duration_ms]}ms</yellow> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            colorize=True,
        )
        error_log_dir = Path(__file__).resolve().parents[5] / "tmp"
        error_log_dir.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(error_log_dir / "errors.log"),
            level="ERROR",
            rotation="10 MB",
            retention="7 days",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{extra[request_id]} | "
                "{extra[duration_ms]}ms | "
                "{name}:{function}:{line} | "
                "{message}\n{exception}"
            ),
        )


@dataclass
class LogRecord:
    message: str
    duration_ms: float = 0.0

    def __post_init__(self) -> None:
        self._start_time: float = time.perf_counter()

    def _emit(self, level: LogLevel, exc: Exception | None = None) -> None:
        data = asdict(self)
        message = data.pop("message")

        extra = {k: v for k, v in data.items() if v}
        if not extra.get("duration_ms"):
            extra["duration_ms"] = round(
                (time.perf_counter() - self._start_time) * 1000, 2
            )

        rid = request_id_var.get()
        extra.setdefault("request_id", rid or "-")

        log = logger.bind(**extra) if extra else logger
        if exc:
            log = log.opt(exception=exc)
        getattr(log, level.lower())(message)

    def trace(self) -> None:
        self._emit(LogLevel.TRACE)

    def debug(self) -> None:
        self._emit(LogLevel.DEBUG)

    def info(self) -> None:
        self._emit(LogLevel.INFO)

    def success(self) -> None:
        self._emit(LogLevel.SUCCESS)

    def warning(self) -> None:
        self._emit(LogLevel.WARNING)

    def error(self, exc: Exception | None = None) -> None:
        self._emit(LogLevel.ERROR, exc=exc)

    def critical(self) -> None:
        self._emit(LogLevel.CRITICAL)
