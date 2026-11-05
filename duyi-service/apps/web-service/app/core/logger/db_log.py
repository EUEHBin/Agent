from dataclasses import dataclass

from app.core.logger.log_record import LogRecord


@dataclass
class DBLog(LogRecord):
    sql: str = ""
    params: str = ""
