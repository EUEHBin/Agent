"""资源不存在异常"""

from app.exception.base import BusinessException


class NotFoundException(BusinessException):
    """资源不存在业务异常"""

    pass
