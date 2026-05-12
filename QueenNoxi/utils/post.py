async def post(url: str, *args, **kwargs):
    import QueenNoxi
    async with QueenNoxi.aiohttpsession.post(url, *args, **kwargs) as resp:
        try:
            data = await resp.json()
        except Exception:
            data = await resp.text()
    return data
