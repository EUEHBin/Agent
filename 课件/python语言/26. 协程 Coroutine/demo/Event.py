import asyncio
from async_delay import async_delay
from gather import gather


# 以下是简易版的实现
class Event:
    def __init__(self):
        self._fut = None

    def set(self):
        if self._fut:
            self._fut.set_result(None)

    async def wait(self):
        loop = asyncio.get_running_loop()
        self._fut = loop.create_future()
        await self._fut


async def test():
    event = Event()

    async def waiter():
        print("waiter: 开始等待")
        await event.wait()
        print("waiter: 被唤醒")

    async def setter():
        print("setter: 1秒后设置事件")
        await async_delay(1)
        event.set()
        print("setter: 事件已设置")

    await gather(waiter(), setter())


if __name__ == "__main__":
    asyncio.run(test())

    """ 
    waiter: 开始等待
    setter: 1秒后设置事件
    setter: 事件已设置
    waiter: 被唤醒 
    """
