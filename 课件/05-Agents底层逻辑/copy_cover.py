import os
import shutil

source_dir = ""

target_dir = ""


def copy_cover(src: str, dst: str) -> None:
    """递归地将源目录内容覆盖合并到目标目录

    文件：直接覆盖
    目录：递归进入处理子内容，不整体替换
    目标目录原有的额外文件/目录保持不变
    """
    if not os.path.exists(dst):
        os.makedirs(dst, exist_ok=True)

    for item in os.listdir(src):
        src_path: str = os.path.join(src, item)
        dst_path: str = os.path.join(dst, item)

        if os.path.isdir(src_path):
            copy_cover(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)


if __name__ == "__main__":
    copy_cover(source_dir, target_dir)
    print("覆盖完成！")
