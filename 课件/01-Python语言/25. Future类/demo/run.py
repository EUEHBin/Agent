import asyncio


def run(func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.call_soon(func)
    loop.run_forever()
