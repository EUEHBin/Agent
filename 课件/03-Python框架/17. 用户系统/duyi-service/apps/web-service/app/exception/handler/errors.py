"""错误码配置

硬编码字典：异常类型 → (业务错误码, HTTP状态码, 默认消息)
"""

from fastapi.exceptions import RequestValidationError

from app.exception.auth import AuthException
from app.exception.database import DatabaseException
from app.exception.not_found import NotFoundException
from app.exception.upload import UploadException

ERROR_MAP: dict[type, tuple[str, int, str]] = {
    RequestValidationError: ("422001", 422, "数据验证错误"),
    DatabaseException: ("422002", 422, "数据验证错误"),
    UploadException: ("422003", 422, "上传数据验证错误"),
    NotFoundException: ("404001", 404, "资源不存在"),
    AuthException: ("401001", 401, "认证失败"),
    Exception: ("500001", 500, "服务器内部错误"),
}


PROTOCOL_ERROR_MAP: dict[int, str] = {
    404: "路径不存在",
    405: "请求方法不允许",
    415: "不支持的媒体类型",
}
