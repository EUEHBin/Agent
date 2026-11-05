"""从 ERROR_MAP 与 PROTOCOL_ERROR_MAP 生成接口文档中展示的错误码说明"""


def generate_error_docs() -> str:
    from app.exception.handler.errors import ERROR_MAP, PROTOCOL_ERROR_MAP

    lines: list[str] = ["## 错误码说明\n"]

    # 业务异常表
    lines.append("### 业务错误\n")
    lines.append("| 业务错误码 | HTTP状态码 | 消息 |")
    lines.append("|-----------|-----------|------|")
    seen: set[str] = set()
    for exc_type, (code, http_status, message) in ERROR_MAP.items():
        if exc_type is Exception:
            continue
        if code not in seen:
            seen.add(code)
            lines.append(f"| {code} | {http_status} | {message} |")

    # 协议异常表
    lines.append("\n### 协议错误\n")
    lines.append("| 错误码 | HTTP状态码 | 消息 |")
    lines.append("|--------|-----------|------|")
    for http_status, message in PROTOCOL_ERROR_MAP.items():
        code = str(http_status)
        lines.append(f"| {code} | {http_status} | {message} |")

    return "\n".join(lines)
