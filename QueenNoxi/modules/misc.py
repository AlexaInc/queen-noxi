from pyrogram import filters, Client, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from QueenNoxi import pbot
from QueenNoxi.modules.helper_funcs.chat_status import user_admin

MARKDOWN_HELP = """
ᴍᴀʀᴋᴅᴏᴡɴ ɪs ᴀ ᴠᴇʀʏ ᴘᴏᴡᴇʀғᴜʟ ғᴏʀᴍᴀᴛᴛɪɴɢ ᴛᴏᴏʟ sᴜᴘᴘᴏʀᴛᴇᴅ ʙʏ ᴛᴇʟᴇɢʀᴀᴍ.

• `_italic_`: ᴡʀᴀᴘᴘɪɴɢ ᴛᴇxᴛ ᴡɪᴛʜ '_' ᴡɪʟʟ ᴘʀᴏᴅᴜᴄᴇ ɪᴛᴀʟɪᴄ ᴛᴇxᴛ
• `*bold*`: ᴡʀᴀᴘᴘɪɴɢ ᴛᴇxᴛ ᴡɪᴛʜ '*' ᴡɪʟʟ ᴘʀᴏᴅᴜᴄᴇ ʙᴏʟᴅ ᴛᴇxᴛ
• ``code``: ᴡʀᴀᴘᴘɪɴɢ ᴛᴇxᴛ ᴡɪᴛʜ '`' ᴡɪʟʟ ᴘʀᴏᴅᴜᴄᴇ ᴍᴏɴᴏsᴘᴀᴄᴇᴅ ᴛᴇxᴛ
• `[text](link)`: ᴄʀᴇᴀᴛᴇ ᴀ ʜʏᴘᴇʀʟɪɴᴋ
• `[text](buttonurl:link)`: ᴄʀᴇᴀᴛᴇ ʟɪɴᴋ ʙᴜᴛᴛᴏɴs
• `[text](buttonurl:link:same)`: ᴍᴜʟᴛɪᴘʟᴇ ʙᴜᴛᴛᴏɴs ᴘᴇʀ ʟɪɴᴇ
"""

@pbot.on_message(filters.command("echo") & filters.group)
@user_admin
async def echo(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        return
    
    msg_to_reply = message.reply_to_message or message
    await msg_to_reply.reply_text(args[1], parse_mode=enums.ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    try:
        await message.delete()
    except:
        pass

@pbot.on_message(filters.command("markdownhelp"))
async def markdown_help(client: Client, message: Message):
    if message.chat.type != enums.ChatType.PRIVATE:
        await message.reply_text(
            "Contact me in PM for markdown help!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Markdown help", url=f"t.me/{(await client.get_me()).username}?start=markdownhelp")
            ]])
        )
        return
    
    await message.reply_text(MARKDOWN_HELP)
    await message.reply_text("Try saving a test note: `/save test *Bold Text* [Google](google.com)`")

__mod_name__ = "Exᴛʀᴀs"
__help__ = """
 ❍ /echo <ᴛᴇxᴛ>: ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴇ sᴀᴍᴇ ᴛᴇxᴛ (ᴀᴅᴍɪɴs ᴏɴʟʏ)
 ❍ /markdownhelp: ǫᴜɪᴄᴋ sᴜᴍᴍᴀʀʏ ᴏғ ʜᴏᴡ ᴍᴀʀᴋᴅᴏᴡɴ ᴡᴏʀᴋs
"""
