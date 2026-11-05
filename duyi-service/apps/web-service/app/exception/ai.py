from app.exception.base import BusinessException


class AiException(BusinessException):
    def __init__(self, message: str, *, detail: str = ""):
        super().__init__(message=message, detail=detail)
