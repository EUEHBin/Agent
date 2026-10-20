import asyncio
import signal


async def main():
    task = asyncio.create_task(asyncio.sleep(10))
    await task


# 按 Ctrl+C 触发 SIGINT，程序会优雅退出而非直接崩溃
asyncio.run(main())
