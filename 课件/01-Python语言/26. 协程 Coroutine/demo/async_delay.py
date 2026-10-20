import asyncio


def async_delay(duration: int):
    loop = asyncio.get_event_loop()
    future = loop.create_future()

    loop.call_later(duration, future.set_result, None)
    return future
