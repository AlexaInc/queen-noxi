import asyncio
from datetime import datetime
import pytz
from pyrogram import filters
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from QueenNoxi import pbot as app, BOT_NAME, BOT_USERNAME
from QueenNoxi.modules.sql.night_mode_sql import (
    add_nightmode,
    get_all_chat_id,
    is_nightmode_indb,
    rmnightmode,
)

async def is_register_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.privileges is not None
    except Exception:
        return False

hehes = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_polls=False,
    can_change_info=False,
    can_invite_users=False,
    can_pin_messages=False
)
openhehe = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_polls=True,
    can_change_info=True,
    can_invite_users=True,
    can_pin_messages=True
)

button_row = InlineKeyboardMarkup([[InlineKeyboardButton('Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ', url=f'https://t.me/{BOT_USERNAME}?startgroup=new')]])

@app.on_message(filters.command("nightmode"))
async def close_ws(_, message):
    if message.chat.type.name == "PRIVATE":
        await message.reply("ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ ᴇɴᴀʙʟᴇ ɴɪɢʜᴛ ᴍᴏᴅᴇ ɪɴ ɢʀᴏᴜᴘꜱ.")
        return
    if not await is_register_admin(message.chat.id, message.from_user.id):
        await message.reply("🤦🏻‍♂️ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ꜱᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ...")
        return

    if is_nightmode_indb(str(message.chat.id)):
        await message.reply("ᴛʜɪꜱ ᴄʜᴀᴛ ɪꜱ ʜᴀꜱ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ ɴɪɢʜᴛ ᴍᴏᴅᴇ")
        return
    add_nightmode(str(message.chat.id))
    await message.reply(
        f"​ᴀᴅᴅᴇᴅ ᴄʜᴀᴛ​ ​​: {message.chat.title} \n​ɪᴅ​: {message.chat.id} ᴛᴏ ᴅᴀᴛᴀʙᴀꜱᴇ. \n**ᴛʜɪꜱ ɢʀᴏᴜᴘ ᴡɪʟʟ ʙᴇ ᴄʟᴏꜱᴇᴅ ᴏɴ 12ᴀᴍ(ɪꜱᴛ) ᴀɴᴅ ᴡɪʟʟ ᴏᴘᴇɴᴇᴅ ᴏɴ 06ᴀᴍ(ɪꜱᴛ)**",
        reply_markup=button_row 
    )

@app.on_message(filters.command("rmnight"))
async def disable_ws(_, message):
    if message.chat.type.name == "PRIVATE":
        await message.reply("ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ ᴅɪꜱᴀʙʟᴇ ɴɪɢʜᴛ ᴍᴏᴅᴇ ɪɴ ɢʀᴏᴜᴘꜱ.")
        return
    if not await is_register_admin(message.chat.id, message.from_user.id):
        await message.reply("🤦🏻‍♂️ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ꜱᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ..")
        return

    if not is_nightmode_indb(str(message.chat.id)):
        await message.reply("ᴛʜɪꜱ ᴄʜᴀᴛ ɪꜱ ​ɴᴏᴛ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ ɴɪɢʜᴛ ᴍᴏᴅᴇ")
        return
    rmnightmode(str(message.chat.id))
    await message.reply(
        f"ʀᴇᴍᴏᴠᴇᴅ ᴄʜᴀᴛ : {message.chat.title} \n​ɪᴅ​:  {message.chat.id} ꜰʀᴏᴍ ᴅᴀᴛᴀʙᴀꜱᴇ."
    )

async def job_close():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await app.send_message(
                int(warner.chat_id),
                f"12:00 ᴀᴍ, ɢʀᴏᴜᴘ ɪꜱ ᴄʟᴏꜱɪɴɢ ᴛɪʟʟ 6 ᴀᴍ.\n ɴɪɢʜᴛ ᴍᴏᴅᴇ ꜱᴛᴀʀᴛᴇᴅ ! \n**ᴘᴏᴡᴇʀᴇᴅ ʙʏ {BOT_NAME}**",
                reply_markup=button_row
            )
            await app.set_chat_permissions(int(warner.chat_id), hehes)
        except Exception:
            pass

async def job_open():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await app.send_message(
                int(warner.chat_id),
                f"06:00 ᴀᴍ, ɢʀᴏᴜᴘ ɪꜱ ᴏᴘᴇɴɪɴɢ.\n**ᴘᴏᴡᴇʀᴇᴅ ʙʏ {BOT_NAME}**",
            )
            await app.set_chat_permissions(int(warner.chat_id), openhehe)
        except Exception:
            pass

async def scheduler_loop():
    tz = pytz.timezone("Asia/Kolkata")
    while True:
        now = datetime.now(tz)
        if now.hour == 23 and now.minute == 59:
            await job_close()
            await asyncio.sleep(60)
        elif now.hour == 6 and now.minute == 1:
            await job_open()
            await asyncio.sleep(60)
        await asyncio.sleep(20)

# Start background task safely without blocking
asyncio.get_event_loop().create_task(scheduler_loop())

__help__ = """
*ᴀᴅᴍɪɴs ᴏɴʟʏ*

 ❍ /nightmode *:* ᴀᴅᴅs ɢʀᴏᴜᴘ ᴛᴏ ɴɪɢʜᴛᴍᴏᴅᴇ ᴄʜᴀᴛs
 ❍ /rmnight *:* ʀᴇᴍᴏᴠᴇs ɢʀᴏᴜᴘ ғʀᴏᴍ ɴɪɢʜᴛᴍᴏᴅᴇ ᴄʜᴀᴛs

*ɴᴏᴛᴇ:* ɴɪɢʜᴛ ᴍᴏᴅᴇ ᴄʜᴀᴛs ɢᴇᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴄʟᴏsᴇᴅ ᴀᴛ 12 ᴀᴍ(ɪsᴛ) ᴀɴᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴏᴘᴇɴɴᴇᴅ ᴀᴛ 6 ᴀᴍ(ɪsᴛ) ᴛᴏ ᴘʀᴇᴠᴇɴᴛ ɴɪɢʜᴛ sᴘᴀᴍs.
"""

__mod_name__ = "Nɪɢʜᴛ​"
