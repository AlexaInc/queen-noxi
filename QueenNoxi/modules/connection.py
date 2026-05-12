import re
from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.errors import BadRequest, Unauthorized

import QueenNoxi.modules.sql.connection_sql as sql
from QueenNoxi import DEV_USERS, DRAGONS, pbot
from QueenNoxi.modules.disable import DisableAbleCommandHandler
from QueenNoxi.modules.helper_funcs.chat_status import user_admin

@pbot.on_message(filters.command("allowconnect") & filters.group)
@user_admin
async def allow_connections(client: Client, message: Message):
    chat = message.chat
    args = message.command[1:]
    
    if not args:
        status = sql.allow_connect_to_chat(chat.id)
        await message.reply_text(f"Connection status: {'Allowed' if status else 'Disabled'}")
        return

    if args[0].lower() in ("yes", "on", "true"):
        sql.set_allow_connect_to_chat(chat.id, True)
        await message.reply_text("Connection allowed!")
    elif args[0].lower() in ("no", "off", "false"):
        sql.set_allow_connect_to_chat(chat.id, False)
        await message.reply_text("Connection disabled.")
    else:
        await message.reply_text("Please use 'on' or 'off'.")

@pbot.on_message(filters.command("connect") & filters.private)
async def connect_chat(client: Client, message: Message):
    user = message.from_user
    args = message.command[1:]
    
    if not args:
        await message.reply_text("Please provide a chat ID to connect to.")
        return

    chat_id = args[0]
    try:
        chat_id = int(chat_id)
    except ValueError:
        pass # could be username

    try:
        chat = await client.get_chat(chat_id)
    except Exception as e:
        await message.reply_text(f"Invalid chat! Error: {e}")
        return

    try:
        member = await chat.get_member(user.id)
    except Exception:
        await message.reply_text("You are not a member of that chat!")
        return

    is_admin = member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER)
    is_allow = sql.allow_connect_to_chat(chat.id)

    if is_admin or (is_allow and user.id not in DRAGONS): # Simplify logic
        if sql.connect(user.id, chat.id):
            await message.reply_text(f"Successfully connected to **{chat.title}**.")
            sql.add_history_conn(user.id, str(chat.id), chat.title)
        else:
            await message.reply_text("Connection failed!")
    else:
        await message.reply_text("Connection to this chat is not allowed or you are not an admin!")

@pbot.on_message(filters.command("disconnect") & filters.private)
async def disconnect_chat(client: Client, message: Message):
    if sql.disconnect(message.from_user.id):
        await message.reply_text("Disconnected from chat!")
    else:
        await message.reply_text("You're not connected!")

@pbot.on_message(filters.command("connection") & filters.private)
async def connection_chat(client: Client, message: Message):
    conn = sql.get_connected_chat(message.from_user.id)
    if conn:
        try:
            chat = await client.get_chat(conn.chat_id)
            await message.reply_text(f"You are currently connected to **{chat.title}** (`{chat.id}`).")
        except:
            await message.reply_text("You are connected to an inaccessible chat.")
    else:
        await message.reply_text("You are not connected to any chat.")

CONN_HELP = """
*ᴀᴄᴛɪᴏɴs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴡɪᴛʜ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘs:*

 • ᴠɪᴇᴡ ᴀɴᴅ ᴇᴅɪᴛ ɴᴏᴛᴇs.
 • ᴠɪᴇᴡ ᴀɴᴅ ᴇᴅɪᴛ ғɪʟᴛᴇʀs.
 • ɢᴇᴛ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ᴏғ ᴄʜᴀᴛ.
 • sᴇᴛ ᴀɴᴅ ᴄᴏɴᴛʀᴏʟ ᴀɴᴛɪғʟᴏᴏᴅ sᴇᴛᴛɪɴɢs.
 • sᴇᴛ ᴀɴᴅ ᴄᴏɴᴛʀᴏʟ ʙʟᴀᴄᴋʟɪsᴛ sᴇᴛᴛɪɴɢs.
 • sᴇᴛ ʟᴏᴄᴋs ᴀɴᴅ ᴜɴʟᴏᴄᴋs ɪɴ ᴄʜᴀᴛ.
 • ᴇɴᴀʙʟᴇ ᴀɴᴅ ᴅɪsᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs ɪɴ ᴄʜᴀᴛ.
 • ᴇxᴘᴏʀᴛ ᴀɴᴅ ɪᴍᴘᴏʀᴛ sᴇᴛᴛɪɴɢs.
"""

@pbot.on_message(filters.command("helpconnect") & filters.private)
async def help_connect_chat(client: Client, message: Message):
    await message.reply_text(CONN_HELP)

@pbot.on_callback_query(filters.regex(r"^connect_"))
async def connect_button(client: Client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    
    if data == "connect_disconnect":
        if sql.disconnect(user_id):
            await query.message.edit_text("Disconnected from chat!")
        else:
            await query.answer("You're not connected!", show_alert=True)
            
    elif data == "connect_clear":
        sql.clear_history_conn(user_id)
        await query.message.edit_text("Connection history cleared.")
        
    elif data == "connect_close":
        await query.message.delete()

async def connected(client: Client, message: Message, user_id: int, need_admin: bool = True):
    if message.chat.type != enums.ChatType.PRIVATE:
        return message.chat.id
        
    conn = sql.get_connected_chat(user_id)
    if not conn:
        return False
        
    chat_id = conn.chat_id
    try:
        member = await client.get_chat_member(chat_id, user_id)
    except Exception:
        sql.disconnect(user_id)
        return False

    is_admin = member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER)
    if need_admin and not is_admin and user_id not in DRAGONS:
        await message.reply_text("You must be an admin in the connected group!")
        return False
        
    return chat_id

__mod_name__ = "Cᴏɴɴᴇᴄᴛ"
__help__ = """
sᴏᴍᴇᴛɪᴍᴇs, ʏᴏᴜ ᴊᴜsᴛ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ sᴏᴍᴇ ɴᴏᴛᴇs ᴀɴᴅ ғɪʟᴛᴇʀs ᴛᴏ ᴀ ɢʀᴏᴜᴘ ᴄʜᴀᴛ, ʙᴜᴛ ʏᴏᴜ ᴅᴏɴ'ᴛ ᴡᴀɴᴛ ᴇᴠᴇʀʏᴏɴᴇ ᴛᴏ sᴇᴇ; ᴛʜɪs ɪs ᴡʜᴇʀᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴs ᴄᴏᴍᴇ ɪɴ...
ᴛʜɪs ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ᴀ ᴄʜᴀᴛ's ᴅᴀᴛᴀʙᴀsᴇ, ᴀɴᴅ ᴀᴅᴅ ᴛʜɪɴɢs ᴛᴏ ɪᴛ ᴡɪᴛʜᴏᴜᴛ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅs ᴀᴘᴘᴇᴀʀɪɴɢ ɪɴ ᴄʜᴀᴛ! 

 ❍ /connect <ᴄʜᴀᴛ ɪᴅ>: ᴄᴏɴɴᴇᴄᴛs ᴛᴏ ᴄʜᴀᴛ (PW only)
 ❍ /connection: ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴄʜᴀᴛ ɪɴғᴏ
 ❍ /disconnect: ᴅɪsᴄᴏɴɴᴇᴄᴛ ғʀᴏᴍ ᴀ ᴄʜᴀᴛ
 ❍ /helpconnect: ʟɪsᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs ᴛʜᴀᴛ ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ʀᴇᴍᴏᴛᴇʟʏ

*ᴀᴅᴍɪɴ ᴏɴʟʏ:*
 ❍ /allowconnect <ʏᴇs/ɴᴏ>: ᴀʟʟᴏᴡ ᴀ ᴜsᴇʀ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ᴀ ᴄʜᴀᴛ
"""
