from app.exception.base import BusinessException


class DatabaseException(BusinessException):
    """数据库操作异常，如唯一约束冲突、外键约束冲突等"""
    pass
