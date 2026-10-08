from pathlib import Path


def print_directory_tree(path: Path, prefix: str = "", max_depth: int = -1):
    """
    以树形结构打印目录内容。

    Args:
        path: 要遍历的目录路径 (Path对象)
        prefix: 用于控制每行缩进和连接线的前缀 (递归内部使用)
        max_depth: 最大遍历深度，-1表示不限制
    """
    # 当前深度，用于控制遍历深度
    current_depth = prefix.count("│   ") if "│" in prefix else 0
    if max_depth != -1 and current_depth >= max_depth:
        return

    # 获取目录下的所有条目，并排序（目录在前，文件在后）
    entries = list(path.iterdir())
    dirs = [e for e in entries if e.is_dir()]
    files = [e for e in entries if e.is_file()]

    # 排序：目录和文件各自按名称排序，然后合并，让目录显示在前面
    sorted_entries = sorted(dirs, key=lambda e: e.name) + sorted(
        files, key=lambda e: e.name
    )

    for index, entry in enumerate(sorted_entries):
        # 判断当前条目是否为最后一个，以决定使用 '└── ' 还是 '├── '
        is_last = index == len(sorted_entries) - 1
        connector = "└── " if is_last else "├── "

        # 打印当前条目
        print(f"{prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}")

        # 如果是目录，递归打印其内容，并更新前缀
        if entry.is_dir():
            extension = "    " if is_last else "│   "
            print_directory_tree(entry, prefix + extension, max_depth)


# 使用示例：打印当前目录的结构，深度限制为2层
if __name__ == "__main__":
    target_dir = Path("/Users/yuanjin/工作/课/录播课/AI/Python For Agent")
    print(target_dir.resolve())  # 打印起始目录的完整路径
    print_directory_tree(target_dir, max_depth=2)
