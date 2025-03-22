
import asyncio


async def test(name):
    print(name)
    await asyncio.sleep(1)
    print(name)

async def doit():
    test1 = test("test1")
    test2 = test("test2")
    await asyncio.gather(test1, test2)

asyncio.run(doit())