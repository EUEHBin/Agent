import asyncio
from src.decomposer import decompose
from src.worker import execute_subtask
from src.merger import merge_results
from src.summarizer import summarize
from src.reporter import save_report


async def run_pipeline(topic: str) -> str:
    print("=" * 56)
    print("  多智能体协同调研系统")
    print("=" * 56)
    print(f"\n[调研需求] {topic}\n")

    print("[步骤 1/4] 正在分解调研任务...")
    subtasks: list[str] = await decompose(topic)
    print(f"  共分解为 {len(subtasks)} 个子任务:\n")
    for i, task in enumerate(subtasks, 1):
        print(f"  {i}. {task}")
    print()

    print("[步骤 2/4] 正在并行执行子任务...\n")
    raw_results: list[str | BaseException] = await asyncio.gather(
        *[execute_subtask(i + 1, len(subtasks), task) for i, task in enumerate(subtasks)],
        return_exceptions=True,
    )
    results: list[str] = []
    for r in raw_results:
        if isinstance(r, BaseException):
            results.append(f"[执行失败] {r}")
        else:
            results.append(r)
    print()

    print("[步骤 3/4] 正在合并并生成最终报告...")
    merged: str = merge_results(topic, subtasks, results)
    report: str = await summarize(topic, merged)
    print("  报告生成完成\n")

    print("[步骤 4/4] 正在保存报告...")
    filepath: str = await save_report(topic, report)
    print(f"\n全部完成！报告已保存至: {filepath}")

    return filepath
