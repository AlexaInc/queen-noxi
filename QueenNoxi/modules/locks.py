import html
from alphabet_detector import AlphabetDetector
from pyrogram import filters, Client, enums
from pyrogram.types import (
    ChatPermissions,
    Message,
)
from pyrogram.errors import BadRequest

import QueenNoxi.modules.sql.locks_sql as sql
from QueenNoxi import pbot, LOGGER
from QueenNoxi.modules.helper_funcs.chat_status import (
    can_restrict,
    connection_status,
    user_admin,
    is_user_admin,
)

ad = AlphabetDetector()

LOCK_TYPES = {
    "audio": filters.audio,
    "voice": filters.voice,
    "contact": filters.contact,
    "video": filters.video,
    "videonote": filters.video_note,
    "document": filters.document,
    "sticker": filters.sticker,
    "animation": filters.animation,
    "url": filters.regex(r"(?i)http|t.me"),
    "bots": filters.new_chat_members,
    "forward": filters.forwarded,
    "game": filters.game,
    "location": filters.location,
}

@pbot.on_message(filters.command("locktypes") & filters.group)
async def locktypes(client: Client, message: Message):
    await message.reply_text(
        "Available lock types:\n\n" + "\n".join([f" • {l}" for l in LOCK_TYPES.keys()])
    )

@pbot.on_message(filters.command("lock") & filters.group)
@connection_status
@user_admin
@can_restrict
async def lock(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        await message.reply_text("You didn't specify what to lock!")
        return

    lock_type = args[1].lower()
    chat_id = message.chat.id

    if lock_type == "all":
        await client.set_chat_permissions(chat_id, ChatPermissions(can_send_messages=False))
        await message.reply_text("Locked all messages!")
    elif lock_type in LOCK_TYPES:
        sql.update_lock(chat_id, lock_type, True)
        await message.reply_text(f"Locked {lock_type}!")
    else:
        await message.reply_text("Invalid lock type!")

@pbot.on_message(filters.command("unlock") & filters.group)
@connection_status
@user_admin
@can_restrict
async def unlock(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        await message.reply_text("You didn't specify what to unlock!")
        return

    lock_type = args[1].lower()
    chat_id = message.chat.id

    if lock_type == "all":
        await client.set_chat_permissions(
            chat_id, 
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
            )
        )
        await message.reply_text("Unlocked all messages!")
    elif lock_type in LOCK_TYPES:
        sql.update_lock(chat_id, lock_type, False)
        await message.reply_text(f"Unlocked {lock_type}!")
    else:
        await message.reply_text("Invalid lock type!")

@pbot.on_message(filters.group, group=1)
async def del_lockables(client: Client, message: Message):
    if not message.chat or message.chat.type in (enums.ChatType.PRIVATE, enums.ChatType.CHANNEL):
        return

    if await is_user_admin(message.chat, message.from_user.id):
        return

    chat_id = message.chat.id
    locks = sql.get_locks(chat_id)
    if not locks:
        return

    should_del = False
    if locks.audio and message.audio: should_del = True
    elif locks.voice and message.voice: should_del = True
    elif locks.contact and message.contact: should_del = True
    elif locks.video and message.video: should_del = True
    elif locks.videonote and message.video_note: should_del = True
    elif locks.document and message.document: should_del = True
    elif locks.sticker and message.sticker: should_del = True
    elif locks.animation and message.animation: should_del = True
    elif locks.forward and (message.forward_from or message.forward_from_chat): should_del = True
    elif locks.location and message.location: should_del = True
    elif locks.url and (message.entities and any(e.type in (enums.MessageEntityType.URL, enums.MessageEntityType.TEXT_LINK) for e in message.entities)): should_del = True

    if should_del:
        try:
            await message.delete()
        except Exception:
            pass

@pbot.on_message(filters.command("locks") & filters.group)
@connection_status
async def list_locks(client: Client, message: Message):
    chat_id = message.chat.id
    locks = sql.get_locks(chat_id)
    
    res = "<b>Current locks in this chat:</b>\n"
    if locks:
        if locks.audio: res += " • audio\n"
        if locks.voice: res += " • voice\n"
        if locks.contact: res += " • contact\n"
        if locks.video: res += " • video\n"
        if locks.videonote: res += " • videonote\n"
        if locks.document: res += " • document\n"
        if locks.sticker: res += " • sticker\n"
        if locks.animation: res += " • animation\n"
        if locks.url: res += " • url\n"
        if locks.forward: res += " • forward\n"
        if locks.bots: res += " • bots\n"
        if locks.game: res += " • game\n"
        if locks.location: res += " • location\n"
    
    perms = (await client.get_chat(chat_id)).permissions
    res += "\n<b>Chat permissions:</b>\n"
    res += f" • messages: {perms.can_send_messages}\n"
    res += f" • media: {perms.can_send_media_messages}\n"
    res += f" • polls: {perms.can_send_polls}\n"
    res += f" • other: {perms.can_send_other_messages}\n"
    res += f" • previews: {perms.can_add_web_page_previews}\n"

    await message.reply_text(res)

__mod_name__ = "Locks"
__help__ = """
 • `/lock <type>`: Lock a certain type of message.
 • `/unlock <type>`: Unlock a certain type of message.
 • `/locks`: List active locks.
 • `/locktypes`: List available lock types.

Types: `audio`, `voice`, `contact`, `video`, `videonote`, `document`, `sticker`, `animation`, `url`, `forward`, `bots`, `game`, `location`, `all`.
"""
