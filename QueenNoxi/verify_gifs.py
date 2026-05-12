import asyncio
import aiohttp

urls = [
    "https://raw.githubusercontent.com/Abishnoi69/QueenNoxi/main/QueenNoxi/resources/hacking.gif",
    "https://raw.githubusercontent.com/Abishnoi69/QueenNoxi/main/QueenNoxi/resources/police.gif",
    "https://raw.githubusercontent.com/Abishnoi69/QueenNoxi/main/QueenNoxi/resources/bomb.gif",
    "https://raw.githubusercontent.com/Abishnoi69/QueenNoxi/main/QueenNoxi/resources/sleep.gif",
    "https://raw.githubusercontent.com/Abishnoi69/QueenNoxi/main/QueenNoxi/resources/brain.gif",
    "https://raw.githubusercontent.com/Abishnoi69/QueenNoxi/main/QueenNoxi/resources/clock.gif"
]

async def verify():
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                async with session.get(url, timeout=10) as resp:
                    print(f"{url}: {resp.status} - {resp.headers.get('Content-Type')}")
            except Exception as e:
                print(f"{url}: FAILED - {e}")

asyncio.run(verify())
