import html
from pyrogram import filters, Client, enums
from pyrogram.types import Message, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import QueenNoxi.modules.sql.antiflood_sql as sql
from QueenNoxi.modules.sql.approve_sql import is_approved
from QueenNoxi import TIGERS, WOLVES, pbot, LOGGER
from QueenNoxi.modules.helper_funcs.chat_status import bot_admin, is_user_admin, user_admin, user_admin_no_reply
from QueenNoxi.modules.helper_funcs.string_handling import extract_time
from QueenNoxi.modules.connection import connected
from QueenNoxi.modules.log_channel import loggable

FLOOD_GROUP = 3

@pbot.on_message(filters.group & ~filters.service, group=FLOOD_GROUP)
async def check_flood(client: Client, message: Message):
    user = message.from_user
    chat = message.chat
    if not user: return

    # Admin/Whitelist/Approved ignore
    if await is_user_admin(chat, user.id) or user.id in WOLVES or user.id in TIGERS:
        sql.update_flood(chat.id, None)
        return

    if is_approved(chat.id, user.id):
        sql.update_flood(chat.id, None)
        return

    should_ban = sql.update_flood(chat.id, user.id)
    if not should_ban: return

    try:
        getmode, getvalue = sql.get_flood_setting(chat.id)
        msg_text = ""
        
        if getmode == 1: # Ban
            await chat.ban_member(user.id)
            msg_text = f"Banned {user.mention} for flooding!"
        elif getmode == 2: # Kick
            await chat.unban_member(user.id)
            msg_text = f"Kicked {user.mention} for flooding!"
        elif getmode == 3: # Mute
            await chat.restrict_member(user.id, ChatPermissions(can_send_messages=False))
            msg_text = f"Muted {user.mention} for flooding!"
        elif getmode == 4: # Tban
            bantime = await extract_time(message, getvalue)
            await chat.ban_member(user.id, until_date=bantime)
            msg_text = f"Banned {user.mention} for {getvalue} (flooding)!"
        elif getmode == 5: # Tmute
            mutetime = await extract_time(message, getvalue)
            await chat.restrict_member(user.id, ChatPermissions(can_send_messages=False), until_date=mutetime)
            msg_text = f"Muted {user.mention} for {getvalue} (flooding)!"

        if msg_text:
            await message.reply_text(msg_text)
            
    except Exception as e:
        LOGGER.warning(f"Error in antiflood: {e}")

@pbot.on_message(filters.command("setflood") & filters.group)
@user_admin
async def set_flood(client: Client, message: Message):
    chat = message.chat
    args = message.command[1:]

    if not args:
        limit = sql.get_flood_limit(chat.id)
        await message.reply_text(f"Current flood limit: {limit if limit > 0 else 'Disabled'}")
        return

    val = args[0].lower()
    if val in ("off", "no", "0"):
        sql.set_flood(chat.id, 0)
        await message.reply_text("Antiflood disabled.")
    elif val.isdigit():
        limit = int(val)
        if limit < 3 and limit != 0:
            await message.reply_text("Flood limit must be 0 or greater than 3.")
            return
        sql.set_flood(chat.id, limit)
        await message.reply_text(f"Flood limit updated to {limit}.")
    else:
        await message.reply_text("Use `/setflood <number>` or `/setflood off`.")

@pbot.on_message(filters.command("flood") & filters.group)
async def flood(client: Client, message: Message):
    limit = sql.get_flood_limit(message.chat.id)
    if limit == 0:
        await message.reply_text("Antiflood is not enabled here.")
    else:
        await message.reply_text(f"Antiflood is currently set to {limit} consecutive messages.")

@pbot.on_message(filters.command("setfloodmode") & filters.group)
@user_admin
async def set_flood_mode(client: Client, message: Message):
    chat = message.chat
    args = message.command[1:]

    if not args:
        mode, val = sql.get_flood_setting(chat.id)
        modes = ["Off", "Ban", "Kick", "Mute", "Tban", "Tmute"]
        await message.reply_text(f"Current flood mode: {modes[mode]} {f'({val})' if mode > 3 else ''}")
        return

    mode = args[0].lower()
    if mode == "ban":
        sql.set_flood_strength(chat.id, 1, "0")
        await message.reply_text("Flood mode: BAN.")
    elif mode == "kick":
        sql.set_flood_strength(chat.id, 2, "0")
        await message.reply_text("Flood mode: KICK.")
    elif mode == "mute":
        sql.set_flood_strength(chat.id, 3, "0")
        await message.reply_text("Flood mode: MUTE.")
    elif mode == "tban":
        if len(args) < 2:
            await message.reply_text("Specify time (e.g., 5m, 1h).")
            return
        sql.set_flood_strength(chat.id, 4, args[1])
        await message.reply_text(f"Flood mode: TBAN for {args[1]}.")
    elif mode == "tmute":
        if len(args) < 2:
            await message.reply_text("Specify time (e.g., 5m, 1h).")
            return
        sql.set_flood_strength(chat.id, 5, args[1])
        await message.reply_text(f"Flood mode: TMUTE for {args[1]}.")
    else:
        await message.reply_text("Use: ban/kick/mute/tban/tmute")

__mod_name__ = "Fʟᴏᴏᴅ"
