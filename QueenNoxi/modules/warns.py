import html
import re
from typing import Optional

from pyrogram import filters, Client, enums
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
)
from pyrogram.errors import BadRequest

from QueenNoxi import TIGERS, WOLVES, pbot, BOT_ID
from QueenNoxi.modules.disable import DisableAbleCommandHandler
from QueenNoxi.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    is_user_admin,
    user_admin,
    user_admin_no_reply,
)
from QueenNoxi.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from QueenNoxi.modules.helper_funcs.string_handling import split_quotes
from QueenNoxi.modules.log_channel import loggable
from QueenNoxi.modules.sql import warns_sql as sql

WARN_HANDLER_GROUP = 9

async def warn(
    user: User,
    chat_id: int,
    reason: str,
    message: Message,
    warner: User = None,
) -> str:
    if await is_user_admin(message.chat, user.id):
        return

    if user.id in TIGERS:
        await message.reply_text("Tigers can't be warned.")
        return
    if user.id in WOLVES:
        await message.reply_text("Wolves are warn immune.")
        return

    warner_tag = warner.mention if warner else "Automated warn filter."
    limit, soft_warn = sql.get_warn_setting(chat_id)
    num_warns, reasons = sql.warn_user(user.id, chat_id, reason)

    if num_warns >= limit:
        sql.reset_warns(user.id, chat_id)
        if soft_warn:  # punch (kick)
            await message.chat.unban_member(user.id)
            reply = f"<b>Punch Event</b>\n<b>User:</b> {user.mention}\n<b>Count:</b> {limit}"
        else:  # ban
            await message.chat.ban_member(user.id)
            reply = f"<b>Ban Event</b>\n<b>User:</b> {user.mention}\n<b>Count:</b> {limit}"

        for r in reasons:
            reply += f"\n - {html.escape(r or 'No reason')}"
        
        log_reason = f"<b>{html.escape(message.chat.title)}:</b>\n#WARN_BAN\n<b>Admin:</b> {warner_tag}\n<b>User:</b> {user.mention}\n<b>Reason:</b> {reason}\n<b>Counts:</b> {num_warns}/{limit}"
        await message.reply_text(reply)
    else:
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✨ REMOVE ✨", callback_data=f"rm_warn({user.id})")]]
        )
        reply = f"<b>Warn Event</b>\n<b>User:</b> {user.mention}\n<b>Count:</b> {num_warns}/{limit}"
        if reason:
            reply += f"\n<b>Reason:</b> {html.escape(reason)}"
        
        log_reason = f"<b>{html.escape(message.chat.title)}:</b>\n#WARN\n<b>Admin:</b> {warner_tag}\n<b>User:</b> {user.mention}\n<b>Reason:</b> {reason}\n<b>Counts:</b> {num_warns}/{limit}"
        await message.reply_text(reply, reply_markup=keyboard)

    return log_reason

@pbot.on_callback_query(filters.regex(r"rm_warn\((.+?)\)"))
@user_admin_no_reply
@bot_admin
@loggable
async def button(client: Client, query: CallbackQuery) -> str:
    user = query.from_user
    user_id = int(query.data.split("(")[1].split(")")[0])
    chat = query.message.chat
    
    if sql.remove_warn(user_id, chat.id):
        await query.message.edit_text(f"Warn removed by {user.mention}.")
        warned = await client.get_users(user_id)
        return f"<b>{html.escape(chat.title)}:</b>\n#UNWARN\n<b>Admin:</b> {user.mention}\n<b>User:</b> {warned.mention}"
    else:
        await query.answer("User already has no warns.", show_alert=True)
    return ""

@pbot.on_message(filters.command(["warn", "dwarn"]) & filters.group)
@user_admin
@can_restrict
@loggable
async def warn_user(client: Client, message: Message) -> str:
    user_id, reason = await extract_user_and_text(message, message.command[1:])
    if message.command[0].startswith("d") and message.reply_to_message:
        await message.reply_to_message.delete()

    if not user_id:
        await message.reply_text("Invalid user!")
        return ""

    warned = await client.get_users(user_id)
    return await warn(warned, message.chat.id, reason, message, message.from_user)

@pbot.on_message(filters.command(["resetwarn", "resetwarns"]) & filters.group)
@user_admin
@bot_admin
@loggable
async def reset_warns(client: Client, message: Message) -> str:
    user_id = await extract_user(message, message.command[1:])
    if not user_id:
        await message.reply_text("No user designated!")
        return ""

    sql.reset_warns(user_id, message.chat.id)
    await message.reply_text("Warns reset!")
    warned = await client.get_users(user_id)
    return f"<b>{html.escape(message.chat.title)}:</b>\n#RESET_WARN\n<b>Admin:</b> {message.from_user.mention}\n<b>User:</b> {warned.mention}"

@pbot.on_message(filters.command("warns") & filters.group)
async def warns(client: Client, message: Message):
    user_id = await extract_user(message, message.command[1:]) or message.from_user.id
    result = sql.get_warns(user_id, message.chat.id)
    limit, _ = sql.get_warn_setting(message.chat.id)

    if result and result[0] != 0:
        num, reasons = result
        text = f"This user has {num}/{limit} warns."
        if reasons:
            text += "\nReasons:"
            for r in reasons:
                text += f"\n • {r}"
        await message.reply_text(text)
    else:
        await message.reply_text("This user has no warns.")

@pbot.on_message(filters.command("addwarn") & filters.group)
@user_admin
async def add_warn_filter(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2: return
    extracted = split_quotes(args[1])
    if len(extracted) < 2: return

    keyword, content = extracted[0].lower(), extracted[1]
    sql.add_warn_filter(message.chat.id, keyword, content)
    await message.reply_text(f"Warn filter added for '{keyword}'!")

@pbot.on_message(filters.command(["nowarn", "stopwarn"]) & filters.group)
@user_admin
async def remove_warn_filter(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2: return
    keyword = split_quotes(args[1])[0]
    if sql.remove_warn_filter(message.chat.id, keyword):
        await message.reply_text(f"Stopped warning for '{keyword}'.")
    else:
        await message.reply_text("Filter not found.")

@pbot.on_message(filters.command("warnlimit") & filters.group)
@user_admin
@loggable
async def set_warn_limit(client: Client, message: Message) -> str:
    args = message.command[1:]
    if args and args[0].isdigit():
        limit = int(args[0])
        if limit < 3:
            await message.reply_text("Min limit is 3.")
            return ""
        sql.set_warn_limit(message.chat.id, limit)
        await message.reply_text(f"Limit set to {limit}.")
        return f"<b>{html.escape(message.chat.title)}:</b>\n#SET_WARN_LIMIT\n<b>Admin:</b> {message.from_user.mention}\nSet limit to {limit}"
    
    limit, _ = sql.get_warn_setting(message.chat.id)
    await message.reply_text(f"Current limit is {limit}.")
    return ""

@pbot.on_message(filters.command("strongwarn") & filters.group)
@user_admin
async def set_warn_strength(client: Client, message: Message):
    args = message.command[1:]
    if args:
        if args[0].lower() in ("on", "yes"):
            sql.set_warn_strength(message.chat.id, False) # False = ban
            await message.reply_text("Strong warns (ban) enabled.")
        else:
            sql.set_warn_strength(message.chat.id, True) # True = punch
            await message.reply_text("Strong warns disabled (punch).")
    else:
        _, soft = sql.get_warn_setting(message.chat.id)
        await message.reply_text(f"Warns set to {'punch' if soft else 'ban'}.")

@pbot.on_message(filters.text & filters.group, group=WARN_HANDLER_GROUP)
async def warn_filter_msg(client: Client, message: Message):
    chat_id = message.chat.id
    if not message.from_user: return
    triggers = sql.get_chat_warn_triggers(chat_id)
    if not triggers: return

    for trigger in triggers:
        if re.search(rf"( |^|[^\w]){re.escape(trigger)}( |$|[^\w])", message.text, flags=re.IGNORECASE):
            filt = sql.get_warn_filter(chat_id, trigger)
            await warn(message.from_user, chat_id, filt.reply, message)
            break

__mod_name__ = "Warns"
__help__ = """
 • `/warns`: Check user warns.
 • `/warn`: Warn a user.
 • `/resetwarn`: Reset user warns.
 • `/addwarn <keyword> <reply>`: Alert on keyword.
 • `/nowarn <keyword>`: Stop alert.
 • `/warnlimit <num>`: Set limit.
 • `/strongwarn <on/off>`: Ban or kick on limit.
"""
