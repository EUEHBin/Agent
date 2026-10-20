import asyncio

async def async_generator():
    for i in range(3):
        await asyncio.sleep(1)
        yield i

async def main():
    async for i in async_generator():
        print(i)

asyncio.run(main())