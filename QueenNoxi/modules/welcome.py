import html
import random
import re
import time
import asyncio
from pyrogram import filters, Client, enums
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ChatPermissions
)
from pyrogram.errors import RPCError

import QueenNoxi
import QueenNoxi.modules.sql.welcome_sql as sql
from QueenNoxi import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    EVENT_LOGS,
    LOGGER,
    OWNER_IDS,
    TIGERS,
    WOLVES,
    pbot,
    BOT_ID
)
from QueenNoxi.modules.helper_funcs.chat_status import (
    is_user_ban_protected,
    user_admin,
    bot_admin,
    can_restrict,
    connection_status
)
from QueenNoxi.modules.helper_funcs.misc import build_keyboard, revert_buttons
from QueenNoxi.modules.helper_funcs.msg_types import get_welcome_type, Types
from QueenNoxi.modules.helper_funcs.string_handling import (
    escape_invalid_curly_brackets,
    markdown_parser,
)
from QueenNoxi.modules.log_channel import loggable
from QueenNoxi.modules.sql.global_bans_sql import is_user_gbanned

VALID_WELCOME_FORMATTERS = [
    "first",
    "last",
    "fullname",
    "username",
    "id",
    "count",
    "chatname",
    "mention",
]

# Verified user waitlist (for captcha)
VERIFIED_USER_WAITLIST = {}

async def send(message: Message, text: str, keyboard: InlineKeyboardMarkup, backup_message: str):
    chat = message.chat
    cleanserv = sql.clean_service(chat.id)
    reply_to = message.id if not cleanserv else None

    if cleanserv:
        try:
            await message.delete()
        except RPCError:
            pass

    try:
        return await message.reply_text(
            text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
            reply_to_message_id=reply_to
        )
    except RPCError as excp:
        LOGGER.error(f"Error sending welcome: {excp}")
        return await message.reply_text(backup_message)

@pbot.on_message(filters.new_chat_members & filters.group)
@loggable
async def new_member(client: Client, message: Message):
    chat = message.chat
    new_members = message.new_chat_members

    should_welc, cust_welcome, cust_content, welc_type = sql.get_welc_pref(chat.id)
    welc_mutes = sql.welcome_mutes(chat.id)

    for new_mem in new_members:
        if new_mem.id == BOT_ID:
            # Bot joined a new chat
            try:
                await client.send_message(
                    EVENT_LOGS,
                    f"#NEW_GROUP\n**Group Name:** {html.escape(chat.title)}\n**Chat ID:** `{chat.id}`"
                )
            except Exception as e:
                LOGGER.warning(f"Could not send new group log to EVENT_LOGS: {e}")
            await message.reply_text("Watashi ga kita!")
            continue

        if await is_user_gbanned(new_mem.id):
            await chat.ban_member(new_mem.id)
            continue

        # Special welcomes for devs/sudos etc.
        if new_mem.id in OWNER_IDS:
             await message.reply_text("The King has arrived!")
             continue
        elif new_mem.id in DEV_USERS:
             await message.reply_text("One of my creators joined!")
             continue

        if should_welc:
            buttons = sql.get_welc_buttons(chat.id)
            keyb = build_keyboard(buttons)
            keyboard = InlineKeyboardMarkup(keyb)

            first_name = new_mem.first_name or "User"
            last_name = new_mem.last_name or ""
            fullname = f"{first_name} {last_name}".strip()
            count = await chat.get_member_count()
            mention = new_mem.mention
            username = f"@{new_mem.username}" if new_mem.username else mention

            if cust_welcome:
                if cust_welcome == sql.DEFAULT_WELCOME:
                    cust_welcome = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(first=first_name)

                res = cust_welcome.format(
                    first=first_name,
                    last=last_name or first_name,
                    fullname=fullname,
                    username=username,
                    mention=mention,
                    count=count,
                    chatname=chat.title,
                    id=new_mem.id
                )
            else:
                res = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(first=first_name)

            if welc_type == Types.TEXT or welc_type == Types.BUTTON_TEXT:
                sent = await send(message, res, keyboard, "Welcome!")
            else:
                # Handle media welcomes
                sent = await client.send_cached_media(
                    chat.id,
                    cust_content,
                    caption=res,
                    reply_markup=keyboard
                )

            # Clean previous welcome
            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    await client.delete_messages(chat.id, prev_welc)
                except RPCError:
                    pass
            if sent:
                sql.set_clean_welcome(chat.id, sent.id)

        # Handle Welcome Mutes (Captcha)
        if welc_mutes and not await is_user_ban_protected(chat, new_mem.id):
            if welc_mutes == "soft":
                await chat.restrict_member(new_mem.id, ChatPermissions(can_send_messages=True, can_send_media_messages=False))
            elif welc_mutes == "strong":
                 # Implementation of captcha button
                 pass

@pbot.on_message(filters.left_chat_member & filters.group)
async def left_member(client: Client, message: Message):
    chat = message.chat
    user = message.left_chat_member

    if user.id == BOT_ID:
        return

    should_goodbye, cust_goodbye, goodbye_type = sql.get_gdbye_pref(chat.id)
    if should_goodbye:
        first_name = user.first_name or "User"
        res = cust_goodbye.format(first=first_name) if cust_goodbye else f"Goodbye {first_name}!"
        await message.reply_text(res)

@pbot.on_message(filters.command("welcome") & filters.group)
@user_admin
async def welcome(client: Client, message: Message):
    args = message.command[1:]
    chat = message.chat
    
    if not args:
        pref, _, _, _ = sql.get_welc_pref(chat.id)
        await message.reply_text(f"Welcome preference is set to: `{pref}`")
        return

    if args[0].lower() in ("on", "yes"):
        sql.set_welc_preference(chat.id, True)
        await message.reply_text("I'll greet members when they join!")
    elif args[0].lower() in ("off", "no"):
        sql.set_welc_preference(chat.id, False)
        await message.reply_text("I'll stop welcoming people.")

@pbot.on_message(filters.command("setwelcome") & filters.group)
@user_admin
async def set_welcome_msg(client: Client, message: Message):
    chat = message.chat
    text, data_type, content, buttons = await get_welcome_type(message)

    if not data_type:
        await message.reply_text("You didn't specify what to reply with!")
        return

    sql.set_custom_welcome(chat.id, content, text, data_type, buttons)
    await message.reply_text("Successfully set custom welcome message!")

@pbot.on_message(filters.command("resetwelcome") & filters.group)
@user_admin
async def reset_welcome(client: Client, message: Message):
    chat = message.chat
    sql.set_custom_welcome(chat.id, None, sql.DEFAULT_WELCOME, Types.TEXT)
    await message.reply_text("Successfully reset welcome message to default!")

@pbot.on_message(filters.command("cleanservice") & filters.group)
@user_admin
async def cleanservice(client: Client, message: Message):
    args = message.command[1:]
    chat = message.chat
    if not args:
        pref = sql.clean_service(chat.id)
        await message.reply_text(f"Clean service is currently: `{pref}`")
        return
    
    if args[0].lower() in ("on", "yes"):
        sql.set_clean_service(chat.id, True)
        await message.reply_text("I will now clean service messages!")
    else:
        sql.set_clean_service(chat.id, False)
        await message.reply_text("I will no longer clean service messages.")

__mod_name__ = "Welcome"
__help__ = """
Manage welcome and goodbye messages in your group.

**Commands:**
• `/welcome <on/off>`: Toggle greetings
• `/setwelcome <msg>`: Set custom welcome
• `/resetwelcome`: Reset welcome
• `/cleanservice <on/off>`: Clean join/leave messages
"""
