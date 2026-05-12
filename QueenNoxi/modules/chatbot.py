import html
import re
import aiohttp
import asyncio
from pyrogram import filters, Client, enums
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import QueenNoxi.modules.sql.chatbot_sql as sql
from QueenNoxi import BOT_ID, BOT_NAME, BOT_USERNAME, pbot
from QueenNoxi.modules.helper_funcs.chat_status import user_admin
from QueenNoxi.modules.log_channel import gloggable
from MukeshAPI import api

import os
import subprocess

async def get_response(text, user_id="anon", group_id=None):
    try:
        # Use subprocess to call the Node.js bridge
        brain_path = os.path.join(os.getcwd(), "QueenNoxi", "brain", "query.js")
        if not os.path.exists(brain_path):
             brain_path = os.path.join(os.getcwd(), "brain", "query.js")
        
        cmd = ["node", brain_path, "query", text, str(user_id)]
        if group_id:
            cmd.append(str(group_id))

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return stdout.decode().strip()
        else:
            err = stderr.decode().strip()
            return f"Error from Brain: {err}"
    except Exception as e:
        return f"Error calling Brain: {e}"

async def learn_brain(q, a):
    try:
        brain_path = os.path.join(os.getcwd(), "QueenNoxi", "brain", "query.js")
        if not os.path.exists(brain_path):
             brain_path = os.path.join(os.getcwd(), "brain", "query.js")
        
        process = await asyncio.create_subprocess_exec(
            "node", brain_path, "learn", q, a,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return process.returncode == 0
    except Exception:
        return False



@pbot.on_callback_query(filters.regex(r"(add|rm)_chat\("))
@gloggable
async def chatbot_callback(client: Client, query: CallbackQuery):
    user = query.from_user
    chat = query.message.chat
    
    member = await client.get_chat_member(chat.id, user.id)
    if member.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        await query.answer("You must be an admin to do this!", show_alert=True)
        return

    action = query.data.split("_")[0]
    if action == "add":
        sql.rem_queennoxi(chat.id)
        await query.message.edit_text(f"{BOT_NAME} chatbot enabled by {user.mention}.")
        return f"<b>{html.escape(chat.title)}:</b>\nᴀɪ ᴇɴᴀʙʟᴇ\n<b>ᴀᴅᴍɪɴ :</b> {user.mention}\n"
    else:
        sql.set_queennoxi(chat.id)
        await query.message.edit_text(f"{BOT_NAME} chatbot disabled by {user.mention}.")
        return f"<b>{html.escape(chat.title)}:</b>\nᴀɪ ᴅɪsᴀʙʟᴇᴅ\n<b>ᴀᴅᴍɪɴ :</b> {user.mention}\n"

@pbot.on_message(filters.command("chatbot") & filters.group)
@user_admin
async def chatbot_toggle(client: Client, message: Message):
    msg = "• ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="ᴇɴᴀʙʟᴇ", callback_data=f"add_chat({message.from_user.id})"),
                InlineKeyboardButton(text="ᴅɪsᴀʙʟᴇ", callback_data=f"rm_chat({message.from_user.id})"),
            ],
        ]
    )
    await message.reply_text(msg, reply_markup=keyboard)

@pbot.on_message(
    filters.text 
    & ~filters.command(["chatbot"])
    & ~filters.regex(r"^/") 
    & ~filters.regex(r"^#[^\s]+") 
    & ~filters.regex(r"^!") 
    & filters.group
)
async def chatbot_msg(client: Client, message: Message):
    chat_id = message.chat.id
    if sql.is_queennoxi(chat_id):
        return

    should_reply = False
    if message.text.lower() == "queennoxi":
        should_reply = True
    elif f"@{BOT_USERNAME}" in message.text:
        should_reply = True
    elif message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == BOT_ID:
        should_reply = True

    if should_reply:
        await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
        response = await get_response(message.text, message.from_user.id, chat_id)
        if response and response.strip():
            await message.reply_text(response)


@pbot.on_message(filters.command("learn") & filters.reply & filters.group)
@user_admin
async def learn_handler(client: Client, message: Message):
    message_b = message.reply_to_message
    
    # but more reliably we might need to fetch it or check message_b.reply_to_message_id
    
    if not message_b.reply_to_message:
        # If not cached, we can try to get it
        try:
             reply_to = await client.get_messages(message.chat.id, message_b.reply_to_message_id)
             message_a = reply_to
        except Exception:
             await message.reply_text("I couldn't find the original message this was replying to.")
             return
    else:
        message_a = message_b.reply_to_message
    
    q = message_a.text or message_a.caption
    a = message_b.text or message_b.caption
    
    if not q or not a:
        await message.reply_text("Both messages must contain text to learn.")
        return
    
    success = await learn_brain(q, a)
    if success:
        await message.reply_text(f"✅ Learned successfully!\n**Q:** `{q}`\n**A:** `{a}`")
    else:
        await message.reply_text("❌ Failed to learn pattern.")


__mod_name__ = "Chatbot"
__help__ = """
 • `/chatbot`: Toggle chatbot in the group.
"""
