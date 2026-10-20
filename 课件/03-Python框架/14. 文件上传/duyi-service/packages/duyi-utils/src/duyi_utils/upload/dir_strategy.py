from datetime import datetime


def date_uuid_strategy() -> str:
    """
    日期 + UUID 目录策略。

    目录结构包含年月日层级，存放路径格式为：
    {base}/{YYYY}/{MM}/{DD}/

    Args:
        filename: 文件名字符串（未使用，保留以统一策略接口）。

    Returns:
        目录路径字符串，以 / 结尾。

    Examples:
        >>> date_uuid_strategy("photo.png")
        "uploads/2025/06/26/"
    """
    now = datetime.now()
    return f"uploads/{now.year:04d}/{now.month:02d}/{now.day:02d}/"


def flat_uuid_strategy() -> str:
    """
    扁平 UUID 目录策略。

    所有文件放在同一目录下，存放路径格式为：
    {base}/

    Args:
        filename: 文件名字符串（未使用，保留以统一策略接口）。

    Returns:
        目录路径字符串，以 / 结尾。

    Examples:
        >>> flat_uuid_strategy("photo.png")
        "uploads/"
    """
    return "uploads/"
