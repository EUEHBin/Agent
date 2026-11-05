import os


def get_suffix(filename: str) -> str | None:
    """
    根据文件名字符串获取后缀名，不包含英文点号。

    Args:
        filename: 文件名字符串，可以是裸文件名（如 "photo.png"）或路径（如 "/path/to/photo.png"）。

    Returns:
        小写后缀名（如 "png"），不含点号。获取不到则返回 None。

    Examples:
        >>> get_suffix("photo.png")
        "png"
        >>> get_suffix("/path/to/report.PDF")
        "pdf"
        >>> get_suffix("noext")
        None
    """
    ext = os.path.splitext(filename)[1]
    if not ext:
        return None
    return ext.lstrip(".").lower()
