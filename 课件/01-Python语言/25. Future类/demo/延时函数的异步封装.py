import asyncio
import run


def async_delay(duration: int):
    loop = asyncio.get_event_loop()
    future = loop.create_future()

    loop.call_later(duration, future.set_result, None)
    return future


def main():
    async_delay(2).add_done_callback(lambda _: print("2 seconds have passed"))
    print("不影响其他代码的执行")


run.run(main)
