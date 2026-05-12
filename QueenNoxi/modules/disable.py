import importlib
from typing import Union, List
from functools import wraps

from pyrogram import filters, Client, enums
from pyrogram.types import Message

from QueenNoxi import pbot, LOGGER
from QueenNoxi.modules.helper_funcs.chat_status import connection_status, user_admin, is_user_admin
from QueenNoxi.modules.sql import disable_sql as sql
from QueenNoxi.modules.helper_funcs.handlers import SpamChecker, is_user_blacklisted

DISABLE_CMDS = []
DISABLE_OTHER = []
ADMIN_CMDS = []

def DisableAbleCommandHandler(command, callback=None, admin_ok=False, **kwargs):
    def decorator(callback):
        if isinstance(command, str):
            cmds = [command]
        else:
            cmds = command

        for cmd in cmds:
            DISABLE_CMDS.append(cmd)
            if admin_ok:
                ADMIN_CMDS.append(cmd)

        @wraps(callback)
        async def wrapped(client: Client, message: Message, *args, **kwargs):
            if message.from_user:
                user_id = message.from_user.id
                if is_user_blacklisted(user_id):
                    return
                if SpamChecker.check_user(user_id):
                    return

            chat_id = message.chat.id
            cmd_name = message.command[0].lower() if message.command else ""
            
            if sql.is_command_disabled(chat_id, cmd_name):
                if admin_ok and await is_user_admin(message.chat, message.from_user.id):
                    return await callback(client, message, *args, **kwargs)
                return
            
            return await callback(client, message, *args, **kwargs)

        pbot.on_message(filters.command(cmds) & ~filters.forwarded)(wrapped)
        return wrapped

    if callback is not None:
        return decorator(callback)
    return decorator


@pbot.on_message(filters.command("disable") & filters.group)
@connection_status
@user_admin
async def disable(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("What should I disable?")
        return

    disable_cmd = message.command[1].lower()
    if disable_cmd in set(DISABLE_CMDS + DISABLE_OTHER):
        sql.disable_command(message.chat.id, disable_cmd)
        await message.reply_text(f"Disabled the use of `{disable_cmd}`")
    else:
        await message.reply_text("That command can't be disabled")


@pbot.on_message(filters.command("enable") & filters.group)
@connection_status
@user_admin
async def enable(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("What should I enable?")
        return

    enable_cmd = message.command[1].lower()
    if sql.enable_command(message.chat.id, enable_cmd):
        await message.reply_text(f"Enabled the use of `{enable_cmd}`")
    else:
        await message.reply_text("Is that even disabled?")


@pbot.on_message(filters.command(["cmds", "disabled"]) & filters.group)
@connection_status
async def commands(client: Client, message: Message):
    chat_id = message.chat.id
    disabled = sql.get_all_disabled(chat_id)
    if not disabled:
        await message.reply_text("No commands are disabled!")
        return

    result = "The following commands are currently restricted:\n"
    for cmd in disabled:
        result += f" - `{cmd}`\n"
    await message.reply_text(result)


@pbot.on_message(filters.command("listcmds") & filters.group)
@connection_status
@user_admin
async def list_cmds(client: Client, message: Message):
    if DISABLE_CMDS + DISABLE_OTHER:
        result = "The following commands are toggleable:\n"
        for cmd in set(DISABLE_CMDS + DISABLE_OTHER):
            result += f" - `{cmd}`\n"
        await message.reply_text(result)
    else:
        await message.reply_text("No commands can be disabled.")


def __stats__():
    return f"• {sql.num_disabled()} ᴅɪsᴀʙʟᴇᴅ ɪᴛᴇᴍs, ᴀᴄʀᴏss {sql.num_chats()} ᴄʜᴀᴛs."

def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)

__mod_name__ = "Disable"
__help__ = """
» /cmds: Check the current status of disabled commands

*Admins only:*
» /enable <cmd name>: Enable that command
» /disable <cmd name>: Disable that command
» /listcmds: List all possible toggleable commands
"""
