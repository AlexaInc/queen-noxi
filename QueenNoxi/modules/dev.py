import os
import subprocess
import sys
import asyncio
from pyrogram import filters, Client, enums
from pyrogram.types import Message

import QueenNoxi
from QueenNoxi import pbot, OWNER_ID
from QueenNoxi.modules.helper_funcs.chat_status import dev_plus

@pbot.on_message(filters.command("lockdown") & filters.user(OWNER_ID))
@dev_plus
async def allow_groups(client: Client, message: Message):
    args = message.command[1:]
    if not args:
        await message.reply_text(f"Current state: {QueenNoxi.ALLOW_CHATS}")
        return
    
    if args[0].lower() in ("off", "no"):
        QueenNoxi.ALLOW_CHATS = True
    elif args[0].lower() in ("yes", "on"):
        QueenNoxi.ALLOW_CHATS = False
    else:
        await message.reply_text("Format: /lockdown Yes/No or Off/On")
        return
    await message.reply_text("Done! Lockdown value toggled.")

@pbot.on_message(filters.command("leave") & filters.user(OWNER_ID))
@dev_plus
async def leave(client: Client, message: Message):
    args = message.command[1:]
    if args:
        chat_id = args[0]
        try:
            await client.leave_chat(int(chat_id))
            await message.reply_text("Successfully left the chat.")
        except Exception as e:
            await message.reply_text(f"Could not leave chat: {e}")
    else:
        await message.reply_text("Send a valid chat ID.")

@pbot.on_message(filters.command("reboot") & filters.user(OWNER_ID))
@dev_plus
async def restart(client: Client, message: Message):
    await message.reply_text("Starting a new instance and shutting down this one...")
    # These might need adjustment depending on how the bot is actually run
    # For now, keeping the original logic of calling scripts
    if os.name == 'nt': # Windows
        os.system("restart.bat")
    else: # Linux/HuggingFace (scripts might not exist there, but keeping for compatibility)
        os.execv(sys.executable, [sys.executable] + sys.argv)

@pbot.on_message(filters.command("gitpull") & filters.user(OWNER_ID))
@dev_plus
async def gitpull(client: Client, message: Message):
    sent_msg = await message.reply_text("Pulling changes from git...")
    subprocess.Popen("git pull", stdout=subprocess.PIPE, shell=True).wait()
    
    await sent_msg.edit_text("Changes pulled. Restarting in 5 seconds...")
    for i in reversed(range(5)):
        await asyncio.sleep(1)
        await sent_msg.edit_text(f"Restarting in {i+1}...")
    
    await sent_msg.edit_text("Restarting now.")
    if os.name == 'nt':
        os.system("restart.bat")
    else:
        os.execv(sys.executable, [sys.executable] + sys.argv)

__mod_name__ = "Dᴇᴠ"
