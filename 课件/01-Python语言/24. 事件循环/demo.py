import asyncio

loop = asyncio.new_event_loop()


def first():
    print(1)


def second():
    print(2)
    loop.call_soon(lambda: print(3))
    loop.stop()


def third():
    print(4)


loop.call_soon(first)
loop.call_soon(second)
loop.call_soon(third)

loop.run_forever()
print("循环已停止")
