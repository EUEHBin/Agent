from __future__ import annotations


def merge_results(topic: str, subtasks: list[str], results: list[str]) -> str:
    lines: list[str] = [f"# {topic}\n"]
    lines.append("## 子任务分解\n")

    for i, (task, result) in enumerate(zip(subtasks, results), 1):
        lines.append(f"### 子任务{i}: {task}\n")
        if isinstance(result, Exception):
            lines.append(f"该子任务执行失败: {result}\n")
        else:
            lines.append(result)
        lines.append("")

    return "\n".join(lines)
