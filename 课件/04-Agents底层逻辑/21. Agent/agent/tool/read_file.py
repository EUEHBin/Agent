from agent.tool.core import tool


@tool(filepath="文件绝对路径或相对于cwd的路径")
def read_file(filepath: str) -> str:
    """读取文件内容并以字符串形式返回"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
