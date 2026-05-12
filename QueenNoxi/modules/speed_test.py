import speedtest
import asyncio
from pyrogram import filters, Client, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from QueenNoxi import pbot, DEV_USERS

def convert(speed):
    return round(int(speed) / 1048576, 2)

async def run_speedtest():
    loop = asyncio.get_event_loop()
    speed = speedtest.Speedtest()
    await loop.run_in_executor(None, speed.get_best_server)
    await loop.run_in_executor(None, speed.download)
    await loop.run_in_executor(None, speed.upload)
    return speed

@pbot.on_message(filters.command("speedtest"))
async def speedtestxyz(client: Client, message: Message):
    if message.from_user.id not in DEV_USERS:
        await message.reply_text("Only Developers can run speedtests!")
        return

    buttons = [
        [
            InlineKeyboardButton("Image", callback_data="speedtest_image"),
            InlineKeyboardButton("Text", callback_data="speedtest_text"),
        ]
    ]
    await message.reply_text(
        "Choose speedtest mode:", 
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@pbot.on_callback_query(filters.regex(r"^speedtest_"))
async def speedtestxyz_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in DEV_USERS:
        await query.answer("Access Denied!", show_alert=True)
        return

    await query.message.edit_text("Running speedtest... please wait.")
    
    try:
        speed = await run_speedtest()
        if query.data == "speedtest_image":
            loop = asyncio.get_event_loop()
            pic = await loop.run_in_executor(None, speed.results.share)
            await query.message.reply_photo(pic, caption="Speedtest Result")
            await query.message.delete()
        else:
            res = speed.results.dict()
            reply = (
                f"**Speedtest Result**\n"
                f"Download: `{convert(res['download'])} Mb/s`\n"
                f"Upload: `{convert(res['upload'])} Mb/s`\n"
                f"Ping: `{res['ping']} ms`"
            )
            await query.message.edit_text(reply)
    except Exception as e:
        await query.message.edit_text(f"Speedtest failed: {e}")

__mod_name__ = "Speedtest"
__help__ = """
• `/speedtest`: Run server speedtest (Devs only).
"""
