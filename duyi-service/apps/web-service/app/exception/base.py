"""业务异常基类

所有自定义业务异常均从此类派生，上层可通过 ``except BusinessException`` 统一捕获。
"""


class BusinessException(Exception):
    """业务异常基类

    Attributes:
        message: 对外暴露的信息，可展示给用户
        detail: 对内详细信息，供开发人员日志记录和问题排查
        original_exception: 原始异常实例，便于追溯根因
    """

    def __init__(
        self,
        message: str,
        *,
        detail: str = "",
        original_exception: Exception | None = None,
    ):
        self.message = message
        self.detail = detail
        self.original_exception = original_exception
        super().__init__(message)
