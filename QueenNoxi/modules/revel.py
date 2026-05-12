from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import Message
from pyrogram.errors import RPCError
from QueenNoxi import (
    BOT_NAME,
    OWNER_ID,
    START_IMG,
    SUPPORT_CHAT,
    TOKEN,
    pbot,
    MONGO_DB_URI,
    API_ID,
    API_HASH
)

@pbot.on_message(
    filters.command(["con", "var"]) & filters.user(OWNER_ID)
)
async def get_vars(client, message: Message):
    try:
        await client.send_message(
            chat_id=int(OWNER_ID),
            text=f"""<u>**{BOT_NAME} ᴄᴏɴғɪɢ ᴠᴀʀɪᴀʙʟᴇs :**</u>

**ʙᴏᴛ_ᴛᴏᴋᴇɴ :** `{TOKEN}`
**sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ :** `{SUPPORT_CHAT}`
**Sᴛᴀʀᴛ Iᴍᴀɢᴇ :** `{START_IMG}`
**Aᴘɪ Iᴅ :** `{API_ID}`
**Aᴘɪ Hᴀsʜ :** `{API_HASH}` 
**Mᴏɴɢᴏ Uʀʟ :** `{MONGO_DB_URI}`   
""")
    except RPCError:
        return await message.reply_text("» ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ᴛʜᴇ ᴄᴏɴғɪɢ ᴠᴀʀɪᴀʙʟᴇs.")
    
    if message.chat.type != ChatType.PRIVATE:
        await message.reply_text(
            "» ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴘᴍ, ɪ'ᴠᴇ sᴇɴᴛ ᴛʜᴇ ᴄᴏɴғɪɢ ᴠᴀʀɪᴀʙʟᴇs ᴛʜᴇʀᴇ."
        )

__mod_name__ = "Revel"
__help__ = """
**Owner Only:**
• `/con` or `/var`: Get bot config variables (sent in PM)
"""
