import re
import os

__all__: list[str] = ["merge_markdown"]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def _demote_heading(match: re.Match) -> str:
    """将匹配到的标题降级。"""
    hashes, content = match.group(1), match.group(2)
    level = len(hashes)
    if level < 6:
        return f'{"#" * (level + 1)} {content}'
    else:
        return f"**{content}**"


def merge_markdown(files: list[str], output: str) -> None:
    """合并多个 Markdown 文件，所有标题降级一级。"""
    parts: list[str] = ["# 合并结果", ""]

    for filepath in files:
        filepath = os.path.abspath(filepath)
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        demoted = HEADING_RE.sub(_demote_heading, content)
        parts.append(demoted.strip())
        parts.append("")

    output = os.path.abspath(output)
    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(parts).strip() + "\n")
