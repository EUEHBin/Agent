import asyncio
from src.orchestrator import run_pipeline


async def main() -> None:
    topic: str = input("请输入调研需求: ").strip()
    if not topic:
        print("调研需求不能为空")
        return

    await run_pipeline(topic)


if __name__ == "__main__":
    asyncio.run(main())
