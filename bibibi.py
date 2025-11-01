import asyncio


class UwU():
    def __init__(self, uwu):
        self.uwu = uwu
        async def something():
            print(f"I'm doing something... {self.uwu}")
            await asyncio.sleep(2)
            print("still here!")
        self.handler = something

    async def suicide(self):
        print("I'm gonna kill myself")
        await asyncio.sleep(5)

        print("Uhhh, what?")

async def some(a: UwU):
    asyncio.create_task(a.handler())

async def runner():
    while True:
        await asyncio.sleep(1)
        print("hello")

async def main():
    a = UwU(1)
    b = UwU(2)
    asyncio.create_task(a.handler())
    asyncio.create_task(a.suicide())
    del a
    print("oh hey")


async def impor():
    await asyncio.gather(main(), runner())

if __name__ == '__main__':
    asyncio.run(impor())
