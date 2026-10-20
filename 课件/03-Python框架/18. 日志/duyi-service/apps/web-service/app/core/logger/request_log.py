from dataclasses import dataclass

from app.core.logger.log_record import LogRecord


@dataclass
class RequestLog(LogRecord):
    method: str = ""
    path: str = ""
    status_code: int = 0
    client_ip: str = ""
