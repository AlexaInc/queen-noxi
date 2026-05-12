import asyncio
from platform import python_version as pyver
from pyrogram.enums import ChatType
from pyrogram import __version__ as pver
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telethon import __version__ as tver
from QueenNoxi.modules.no_sql.chats_db import add_served_chat
from QueenNoxi.modules.no_sql.users_db import save_id
from QueenNoxi import SUPPORT_CHAT, SUPPORT_CHAT_URL, pbot, BOT_USERNAME, OWNER_ID, BOT_NAME, START_IMG

PHOTO = [
    "https://telegra.ph/file/d2a23fbe48129a7957887.jpg",
    "https://telegra.ph/file/ddf30888de58d77911ee1.jpg",
    "https://telegra.ph/file/268d66cad42dc92ec65ca.jpg",
    "https://telegra.ph/file/13a0cbbff8f429e2c59ee.jpg",
    "https://telegra.ph/file/bdfd86195221e979e6b20.jpg",
]

QueenNoxi = [
    [
        InlineKeyboardButton(text="ᴏᴡɴᴇʀ", user_id=OWNER_ID),
        InlineKeyboardButton(text="ꜱᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT_URL),
    ],
    [
        InlineKeyboardButton(
            text="➕ᴀᴅᴅ ᴍᴇ ᴇʟsᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ➕",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
        ),
    ],
]

@pbot.on_message(filters.command("alive"))
async def alive(client, m: Message):
    await m.delete()
    accha = await m.reply("⚡")
    await asyncio.sleep(0.2)
    await accha.edit("ᴅɪɴɢ ᴅᴏɴɢ ꨄ︎ ᴀʟɪᴠɪɴɢ..")
    await accha.delete()
    await asyncio.sleep(0.3)
    
    umm = await m.reply_sticker(
        "CAACAgUAAxkDAAJHbmLuy2NEfrfh6lZSohacEGrVjd5wAAIOBAACl42QVKnra4sdzC_uKQQ"
    )
    await umm.delete()
    owner = await client.get_users(OWNER_ID)
    await m.reply_photo(
        START_IMG,
        caption=f"""**ʜᴇʏ, ɪ ᴀᴍ 『[{BOT_NAME}](t.me/{BOT_USERNAME})』**
   ━━━━━━━━━━━━━━━━━━━
  » **ᴍʏ ᴏᴡɴᴇʀ :** {owner.mention}
  
  » **ᴛᴇʟᴇᴛʜᴏɴ :** `{tver}`
  
  » **ᴘʏʀᴏɢʀᴀᴍ :** `{pver}`
  
  » **ᴘʏᴛʜᴏɴ :** `{pyver()}`
   ━━━━━━━━━━━━━━━━━━━""",
        reply_markup=InlineKeyboardMarkup(QueenNoxi)
    )

@pbot.on_message(group=1)
async def save_statss(_, m: Message):
    try:
        if m.chat.type == ChatType.PRIVATE:
            await save_id(m.from_user.id)
        else:
            await add_served_chat(m.chat.id)
    except Exception:
        pass
