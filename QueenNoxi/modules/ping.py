import time
import aiohttp
from pyrogram import filters, Client
from pyrogram.types import Message

from QueenNoxi import StartTime, pbot
from QueenNoxi.modules.disable import DisableAbleCommandHandler
from QueenNoxi.modules.helper_funcs.chat_status import sudo_plus
from QueenNoxi.utils.formatter import get_readable_time

sites_list = {
    "Telegram": "https://api.telegram.org",
    "Kaizoku": "https://animekaizoku.com",
    "Kayo": "https://animekayo.com",
    "Jikan": "https://api.jikan.moe/v3",
}



async def ping_func(to_ping: list) -> list:
    ping_result = []
    async with aiohttp.ClientSession() as session:
        for each_ping in to_ping:
            start_time = time.time()
            site_to_ping = sites_list[each_ping]
            try:
                async with session.get(site_to_ping) as response:
                    status_code = response.status
            except Exception:
                status_code = "Error"
            end_time = time.time()
            ping_time = str(round((end_time - start_time), 2)) + "s"

            pinged_site = f"<b>{each_ping}</b>"
            if each_ping == "Kaizoku" or each_ping == "Kayo":
                pinged_site = f'<a href="{sites_list[each_ping]}">{each_ping}</a>'
                ping_time = f"<code>{ping_time} (Status: {status_code})</code>"

            ping_text = f"{pinged_site}: <code>{ping_time}</code>"
            ping_result.append(ping_text)
    return ping_result

@pbot.on_message(filters.command("ping"))
@DisableAbleCommandHandler("ping")
@sudo_plus
async def ping(client: Client, message: Message):
    start_time = time.time()
    reply = await message.reply_text("🏓 ᴘɪɴɢɪɴɢ ʙᴀʙʏ....​")
    end_time = time.time()
    telegram_ping = str(round((end_time - start_time) * 1000, 3)) + " ms"
    uptime = get_readable_time((time.time() - StartTime))

    await reply.edit_text(
        "ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ! ❤️\n"
        "<b>ᴛɪᴍᴇ ᴛᴀᴋᴇɴ:</b> <code>{}</code>\n"
        "<b>ᴜᴘᴛɪᴍᴇ:</b> <code>{}</code>".format(telegram_ping, uptime)
    )

@pbot.on_message(filters.command("pingall"))
@DisableAbleCommandHandler("pingall")
@sudo_plus
async def pingall(client: Client, message: Message):
    to_ping = ["Telegram"]
    pinged_list = await ping_func(to_ping)
    uptime = get_readable_time((time.time() - StartTime))

    reply_msg = "⏱ᴘɪɴɢ ʀᴇsᴜʟᴛs ᴀʀᴇ:\n"
    reply_msg += "\n".join(pinged_list)
    reply_msg += f"\n<b>ᴜᴘᴛɪᴍᴇ:</b> <code>{uptime}</code>"

    await message.reply_text(
        reply_msg, disable_web_page_preview=True
    )

__mod_name__ = "Ping"
__command_list__ = ["ping", "pingall"]
