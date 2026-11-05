from app.exception.base import BusinessException


class UploadException(BusinessException):
    def __init__(self, message: str):
        super().__init__(message=message)
