import os

__all__: list[str] = ["show_tree"]


def _is_hidden(filepath: str) -> bool:
    """判断文件或文件夹是否隐藏"""
    filepath = os.path.abspath(filepath)  # 始终转换为绝对路径
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"路径不存在: {filepath}")
    basename = os.path.basename(filepath)
    return basename.startswith(".")


def show_tree(dir_path: str, show_hidden: bool = False, _prefix: str = "") -> None:
    """以树形递归方式展示目录内容。"""
    path = os.path.abspath(dir_path)  # 始终转换为绝对路径

    if not _prefix:
        root_name = os.path.basename(path) or path
        print(root_name)

    entries = os.listdir(path)
    if not show_hidden:
        entries = [e for e in entries if not _is_hidden(os.path.join(path, e))]

    entries.sort()

    for i, entry in enumerate(entries):
        entry_path = os.path.join(path, entry)
        is_last = i == len(entries) - 1

        connector = "└── " if is_last else "├── "
        print(f"{_prefix}{connector}{entry}")

        if os.path.isdir(entry_path):
            extension = "    " if is_last else "│   "
            show_tree(entry_path, show_hidden, _prefix + extension)
