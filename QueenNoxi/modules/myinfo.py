import asyncio
import re
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from QueenNoxi import pbot as app, BOT_NAME

edit_time = 5
file1 = "https://telegra.ph/file/9a85d0a873e2dd80d278d.jpg"
file2 = "https://telegra.ph/file/9e7815284031452afa9e5.jpg"
file3 = "https://telegra.ph/file/dcc5e003287f69acea368.jpg"
file4 = "https://telegra.ph/file/ed1ce7fee94f46b0f671e.jpg"
file5 = "https://telegra.ph/file/701028ce085ecfa961a36.jpg"

@app.on_message(filters.command("myinfo"))
async def proboyx(_, message):
    firstname = message.from_user.first_name if message.from_user else "Unknown"
    button = InlineKeyboardMarkup([[InlineKeyboardButton("ɪɴғᴏʀᴍᴀᴛɪᴏɴ", callback_data="informations")]])
    msg = await message.reply_photo(
        photo=file2,
        caption=f"ʜᴇʏ {firstname}, \nᴄʟɪᴄᴋ ᴏɴ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ \n ᴛᴏ ɢᴇᴛ ɪɴғᴏ ᴀʙᴏᴜᴛ ʏᴏᴜ",
        reply_markup=button,
    )
    
    for f in [file3, file5, file1, file4, file2, file1, file3, file5, file4]:
        try:
            await asyncio.sleep(edit_time)
            await msg.edit_media(InputMediaPhoto(media=f, caption=f"ʜᴇʏ {firstname}, \nᴄʟɪᴄᴋ ᴏɴ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ \n ᴛᴏ ɢᴇᴛ ɪɴғᴏ ᴀʙᴏᴜᴛ ʏᴏᴜ"), reply_markup=button)
        except Exception:
            pass

@app.on_callback_query(filters.regex(r"^informations$"))
async def callback_query_handler(_, query):
    try:
        user = query.from_user
        LILIE = f"ᴘᴏᴡᴇʀᴇᴅ ʙʏ {BOT_NAME}\n\n"
        LILIE += f"ғɪʀsᴛ ɴᴀᴍᴇ: {user.first_name} \n" + (f"ʟᴀsᴛ ɴᴀᴍᴇ: {user.last_name}\n" if user.last_name else '')
        LILIE += f"ʏᴏᴜ ʙᴏᴛ : {user.is_bot} \n"
        LILIE += f"ʀᴇsᴛʀɪᴄᴛᴇᴅ : {user.is_restricted} \n"
        LILIE += f"ᴜsᴇʀ ɪᴅ: {user.id}\n"
        LILIE += f"ᴜsᴇʀɴᴀᴍᴇ : @{user.username}\n" if user.username else f"ᴜsᴇʀɴᴀᴍᴇ : `{user.username}`\n"
        await query.answer(LILIE, show_alert=True)
    except Exception as e:
        await query.message.reply(f"{e}")

__command_list__ = ["myinfo"]
