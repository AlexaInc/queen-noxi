import html
import re
from pyrogram import filters, Client, enums
from pyrogram.types import Message

import QueenNoxi.modules.sql.blacklist_sql as sql
from QueenNoxi import LOGGER, pbot
from QueenNoxi.modules.disable import DisableAbleCommandHandler
from QueenNoxi.modules.helper_funcs.chat_status import user_admin, connection_status
from QueenNoxi.modules.warns import warn

BLACKLIST_GROUP = 11

@DisableAbleCommandHandler("blacklist", admin_ok=True)
@connection_status
async def blacklist(client: Client, message: Message):
    chat_id = message.chat.id
    triggers = sql.get_chat_blacklist(chat_id)
    if not triggers:
        return await message.reply_text("No blacklist filters active here!")

    res = "Blacklist filters active in this chat:\n"
    for trigger in triggers:
        res += f" • {html.escape(trigger)}\n"
    await message.reply_text(res)

@DisableAbleCommandHandler("addblacklist", admin_ok=True)
@connection_status
@user_admin
async def add_blacklist(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply_text("Give me a keyword!")

    words = args[1].split("\n")
    for word in words:
        trigger = word.strip().lower()
        if trigger:
            sql.add_to_blacklist(message.chat.id, trigger)
    
    await message.reply_text("Added to blacklist!")

@DisableAbleCommandHandler(["unblacklist", "rmblacklist"], admin_ok=True)
@connection_status
@user_admin
async def unblacklist(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply_text("What should I remove?")

    trigger = args[1].strip().lower()
    if sql.rm_from_blacklist(message.chat.id, trigger):
        await message.reply_text(f"Removed '{trigger}' from blacklist.")
    else:
        await message.reply_text("Not found.")

@DisableAbleCommandHandler("blacklistmode", admin_ok=True)
@connection_status
@user_admin
async def blacklist_mode(client: Client, message: Message):
    args = message.command[1:]
    chat_id = message.chat.id
    if args:
        mode = args[0].lower()
        if mode in ("off", "nothing"): sql.set_blacklist_strength(chat_id, 0, "0")
        elif mode == "del": sql.set_blacklist_strength(chat_id, 1, "0")
        elif mode == "warn": sql.set_blacklist_strength(chat_id, 2, "0")
        elif mode == "mute": sql.set_blacklist_strength(chat_id, 3, "0")
        elif mode == "kick": sql.set_blacklist_strength(chat_id, 4, "0")
        elif mode == "ban": sql.set_blacklist_strength(chat_id, 5, "0")
        else:
            return await message.reply_text("Invalid mode!")
        await message.reply_text(f"Blacklist mode set to {mode}.")
    else:
        st, val = sql.get_blacklist_setting(chat_id)
        modes = ["nothing", "del", "warn", "mute", "kick", "ban"]
        await message.reply_text(f"Current blacklist mode: {modes[st]}")

@pbot.on_message(filters.text & filters.group, group=BLACKLIST_GROUP)
async def del_blacklist(client: Client, message: Message):
    chat_id = message.chat.id
    if not message.from_user: return
    
    # Ignore admins
    if await is_user_admin(message.chat, message.from_user.id):
        return

    triggers = sql.get_chat_blacklist(chat_id)
    if not triggers: return

    for trigger in triggers:
        pattern = rf"( |^|[^\w]){re.escape(trigger)}( |$|[^\w])"
        if re.search(pattern, message.text, flags=re.IGNORECASE):
            st, val = sql.get_blacklist_setting(chat_id)
            try:
                if st == 0:
                    return
                await message.delete()
                if st == 1:
                    break  # just delete
                elif st == 2:  # warn
                    await warn(message.from_user, chat_id, f"Blacklist trigger: {trigger}", message)
                elif st == 3:  # mute
                    await message.chat.restrict_member(
                        message.from_user.id,
                        enums.ChatMemberStatus.RESTRICTED,
                        enums.ChatPermissions(can_send_messages=False),
                    )
                elif st == 4:  # kick
                    await message.chat.unban_member(message.from_user.id)
                elif st == 5:  # ban
                    await message.chat.ban_member(message.from_user.id)
            except Exception as e:
                LOGGER.error(f"Error in blacklist: {e}")
            break

async def is_user_admin(chat, user_id: int) -> bool:
    from QueenNoxi.modules.helper_funcs.chat_status import is_user_admin as check_admin
    return await check_admin(chat, user_id)

__mod_name__ = "Blacklist"
__help__ = """
 • `/blacklist`: List blackened words.
 • `/addblacklist <word>`: Blacklist a word.
 • `/unblacklist <word>`: Un-blacklist a word.
 • `/blacklistmode <mode>`: Set punishment.
  
Modes: `off`, `del`, `warn`, `mute`, `kick`, `ban`.
"""
