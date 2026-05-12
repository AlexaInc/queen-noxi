import asyncio
import aiohttp
from MukeshAPI import api

async def test_ai():
    print("Testing ChatGPT...")
    try:
        res = api.chatgpt("Hello")
        print(f"ChatGPT Result: {res}")
    except Exception as e:
        print(f"ChatGPT Failed: {e}")

    print("\nTesting Widipe OpenAI...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://widipe.com/openai?text=Hello", timeout=10) as resp:
                res = await resp.json()
                print(f"Widipe Result: {res}")
        except Exception as e:
            print(f"Widipe Failed: {e}")

    print("\nTesting SimSimi...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://api.simsimi.net/v2/?text=Hello&lc=en", timeout=10) as resp:
                res = await resp.json()
                print(f"SimSimi Result: {res}")
        except Exception as e:
            print(f"SimSimi Failed: {e}")

    print("\nTesting Safone AI...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://api.safone.me/ai?message=Hello", timeout=10) as resp:
                res = await resp.json()
                print(f"Safone Result: {res}")
        except Exception as e:
            print(f"Safone Failed: {e}")

    print("\nTesting Vyturex AI...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://api.vyturex.com/openai?prompt=Hello", timeout=10) as resp:
                res = await resp.json()
                print(f"Vyturex Result: {res}")
        except Exception as e:
            print(f"Vyturex Failed: {e}")

    print("\nTesting GPT4...")
    try:
        res = api.gpt4("Hello")
        print(f"GPT4 Result: {res}")
    except Exception as e:
        print(f"GPT4 Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai())
