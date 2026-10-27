from agent.tool.core import tool


@tool(filepath="文件绝对路径或相对于cwd的路径", content="待写入的内容")
def write_file(filepath: str, content: str) -> None:
    """将内容写入文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
