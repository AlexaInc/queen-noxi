"""
HuggingFace Spaces entrypoint.

HuggingFace Docker Spaces REQUIRE an HTTP server responding on port 7860.
We spin up a minimal aiohttp web server alongside the Telegram bot so the
Space stays healthy. The HTTP server just returns 200 OK on any request.
"""
import asyncio
import os
from aiohttp import web

# Import of QueenNoxi.main is delayed to avoid event loop conflicts


async def health(request):
    return web.Response(text="✅ QueenNoxi is running!", content_type="text/plain")


async def run_web_server():
    port = int(os.environ.get("PORT", 7860))
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"[Web] Health server running on port {port}")


async def run_all():
    # Start web server sequentially (it is non-blocking)
    await run_web_server()
    
    # Delayed import to ensure Pyrogram objects bind to the loop created by asyncio.run()
    from QueenNoxi.__main__ import main
    await main()


if __name__ == "__main__":
    asyncio.run(run_all())
