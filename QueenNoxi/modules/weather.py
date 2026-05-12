import io
import aiohttp
from pyrogram import filters
from QueenNoxi import pbot as app

@app.on_message(filters.command("weather"))
async def _(_, message):
    if getattr(message, "forward_from", None):
        return
    if len(message.command) == 1:
        await message.reply("Please specify a city! e.g., /weather London")
        return
    sample_url = "https://wttr.in/{}.png"
    input_str = message.text.split(None, 1)[1]
    async with aiohttp.ClientSession() as session:
        response_api_zero = await session.get(sample_url.format(input_str))
        response_api = await response_api_zero.read()
        with io.BytesIO(response_api) as out_file:
            out_file.name = "weather.png"
            await message.reply_photo(photo=out_file)

__help__ = """
ɪ ᴄᴀɴ ғɪɴᴅ ᴡᴇᴀᴛʜᴇʀ ᴏғ ᴀʟʟ ᴄɪᴛɪᴇs

 ❍ /weather <ᴄɪᴛʏ>*:* ᴀᴅᴠᴀɴᴄᴇᴅ ᴡᴇᴀᴛʜᴇʀ ᴍᴏᴅᴜʟᴇ, ᴜsᴀɢᴇ sᴀᴍᴇ ᴀs /ᴡᴇᴀᴛʜᴇʀ
 ❍ /weather  ᴍᴏᴏɴ*:* ɢᴇᴛ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs ᴏғ ᴍᴏᴏɴ
"""

__mod_name__ = "Wᴇᴀᴛʜᴇʀ"
