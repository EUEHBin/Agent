import asyncio
from async_delay import async_delay
from typing import Coroutine


def gather(*aws: Coroutine) -> asyncio.Future:
    future = asyncio.Future()
    finish_count = 0  # 已完成的任务数量
    count = len(aws)  # 任务总数
    results = [None] * count  # 存储结果的列表

    def on_done(f: asyncio.Future, idx: int) -> None:
        nonlocal finish_count
        results[idx] = f.result()  # 将结果存储在对应位置
        finish_count += 1
        if finish_count == count:  # 所有任务完成
            future.set_result(results)  # 设置最终结果

    for i, aw in enumerate(aws):
        asyncio.create_task(aw).add_done_callback(lambda f, idx=i: on_done(f, idx))

    return future


async def coro(name: str, duration: int):
    await async_delay(duration)
    return f"{name} 完成"


async def main():
    results = await gather(
        coro("A", 2),
        coro("B", 1),
        coro("C", 3),
    )
    print(results)  # 预期: ['A 完成', 'B 完成', 'C 完成']


asyncio.run(main())
