import html
from pyrogram import filters, Client, enums
from pyrogram.types import Message
from pyrogram.errors import RPCError

from QueenNoxi import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    LOGGER,
    OWNER_IDS,
    TIGERS,
    WOLVES,
    pbot,
    BOT_ID
)
from QueenNoxi.modules.disable import DisableAbleCommandHandler
from QueenNoxi.modules.helper_funcs.chat_status import (
    bot_admin,
    can_delete,
    can_restrict,
    connection_status,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
    user_admin,
    user_can_ban,
)
from QueenNoxi.modules.helper_funcs.extraction import extract_user_and_text
from QueenNoxi.modules.helper_funcs.string_handling import extract_time
from QueenNoxi.modules.log_channel import gloggable, loggable


@pbot.on_message(filters.command(["ban", "sban"]) & filters.group)
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
async def ban(client: Client, message: Message) -> str:
    chat = message.chat
    user = message.from_user
    user_id, reason = await extract_user_and_text(message, message.command[1:])

    if not user_id:
        await message.reply_text("ɪ ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ.")
        return ""

    try:
        member = await chat.get_member(user_id)
    except RPCError:
        await message.reply_text("ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴘᴇʀsᴏɴ.")
        return ""

    if user_id == BOT_ID:
        await message.reply_text("ᴏʜ ʏᴇᴀʜ, ʙᴀɴ ᴍʏsᴇʟғ, ɴᴏᴏʙ!")
        return ""

    if await is_user_ban_protected(chat, user_id, member) and user.id not in DEV_USERS:
        if user_id in OWNER_IDS:
            await message.reply_text("ᴛʀʏɪɴɢ ᴛᴏ ᴘᴜᴛ ᴍᴇ ᴀɢᴀɪɴsᴛ ᴀ ɢᴏᴅ ʟᴇᴠᴇʟ ᴅɪsᴀsᴛᴇʀ ʜᴜʜ?")
        elif user_id in DEV_USERS:
            await message.reply_text("ɪ ᴄᴀɴ'ᴛ ᴀᴄᴛ ᴀɢᴀɪɴsᴛ ᴏᴜʀ ᴏᴡɴ.")
        elif user_id in DRAGONS:
            await message.reply_text("ғɪɢʜᴛɪɴɢ ᴛʜɪs ᴅʀᴀɢᴏɴ ʜᴇʀᴇ ᴡɪʟʟ ᴘᴜᴛ ᴄɪᴠɪʟɪᴀɴ ʟɪᴠᴇs ᴀᴛ ʀɪsᴋ.")
        elif user_id in DEMONS:
            await message.reply_text("ʙʀɪɴɢ ᴀɴ ᴏʀᴅᴇʀ ғʀᴏᴍ ʜᴇʀᴏᴇs ᴀssᴏᴄɪᴀᴛɪᴏɴ ᴛᴏ ғɪɢʜᴛ ᴀ ᴅᴇᴍᴏɴ ᴅɪsᴀsᴛᴇʀ.")
        elif user_id in TIGERS:
            await message.reply_text("ʙʀɪɴɢ ᴀɴ ᴏʀᴅᴇʀ ғʀᴏᴍ ʜᴇʀᴏᴇs ᴀssᴏᴄɪᴀᴛɪᴏɴ ᴛᴏ ғɪɢʜᴛ ᴀ ᴛɪɢᴇʀ ᴅɪsᴀsᴛᴇʀ.")
        elif user_id in WOLVES:
            await message.reply_text("ᴡᴏʟғ ᴀʙɪʟɪᴛɪᴇs ᴍᴀᴋᴇ ᴛʜᴇᴍ ʙᴀɴ ɪᴍᴍᴜɴᴇ!")
        else:
            await message.reply_text("ᴛʜɪs ᴜsᴇʀ ɪs ʙᴀɴ ᴘʀᴏᴛᴇᴄᴛᴇᴅ!")
        return ""

    silent = message.command[0].lower() == "sban"
    if silent and not await can_delete(chat, BOT_ID):
        return ""

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#{'S' if silent else ''}ʙᴀɴɴᴇᴅ\n"
        f"<b>ʙᴀɴɴᴇᴅ ʙʏ:</b> {user.mention}\n"
        f"<b>ᴜsᴇʀ:</b> {member.user.mention}"
    )
    if reason:
        log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {html.escape(reason)}"

    try:
        await chat.ban_member(user_id)
        if silent:
            if message.reply_to_message:
                await message.reply_to_message.delete()
            await message.delete()
            return log

        reply = (
            f"<code>❕</code><b>ʙᴀɴ ᴇᴠᴇɴᴛ</b>\n"
            f"<code> </code><b>•  ʙᴀɴɴᴇᴅ ʙʏ:</b> {user.mention}\n"
            f"<code> </code><b>•  ᴜsᴇʀ:</b> {member.user.mention}"
        )
        if reason:
            reply += f"\n<code> </code><b>•  ʀᴇᴀsᴏɴ:</b> \n{html.escape(reason)}"
        await message.reply_text(reply)
        return log
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")
        return ""


@pbot.on_message(filters.command("tban") & filters.group)
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
async def temp_ban(client: Client, message: Message) -> str:
    chat = message.chat
    user = message.from_user
    user_id, reason = await extract_user_and_text(message, message.command[1:])

    if not user_id:
        await message.reply_text("ɪ ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ.")
        return ""

    try:
        member = await chat.get_member(user_id)
    except RPCError:
        await message.reply_text("ɪ ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
        return ""

    if user_id == BOT_ID:
        await message.reply_text("ɪ'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ ʙᴀɴ ᴍʏsᴇʟғ.")
        return ""

    if await is_user_ban_protected(chat, user_id, member):
        await message.reply_text("ɪ ᴅᴏɴ'ᴛ ғᴇᴇʟ ʟɪᴋᴇ ɪᴛ.")
        return ""

    if not reason:
        await message.reply_text("ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴘᴇᴄɪғɪᴇᴅ ᴀ ᴛɪᴍᴇ ᴛᴏ ʙᴀɴ ᴛʜɪs ᴜsᴇʀ ғᴏʀ!")
        return ""

    split_reason = reason.split(None, 1)
    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = await extract_time(message, time_val)

    if not bantime:
        return ""

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "ᴛᴇᴍᴩ ʙᴀɴ\n"
        f"<b>ʙᴀɴɴᴇᴅ ʙʏ:</b> {user.mention}\n"
        f"<b>ᴜsᴇʀ:</b> {member.user.mention}\n"
        f"<b>ᴛɪᴍᴇ:</b> {time_val}"
    )
    if reason:
        log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {html.escape(reason)}"

    try:
        await chat.ban_member(user_id, until_date=bantime)
        await message.reply_text(
            f"ʙᴀɴɴᴇᴅ! ᴜsᴇʀ {member.user.mention} ɪs ɴᴏᴡ ʙᴀɴɴᴇᴅ ғᴏʀ {time_val}."
        )
        return log
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")
        return ""


@pbot.on_message(filters.command("kick") & filters.group)
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
async def kick(client: Client, message: Message) -> str:
    chat = message.chat
    user = message.from_user
    user_id, reason = await extract_user_and_text(message, message.command[1:])

    if not user_id:
        await message.reply_text("ɪ ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ.")
        return ""

    try:
        member = await chat.get_member(user_id)
    except RPCError:
        await message.reply_text("ɪ ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
        return ""

    if user_id == BOT_ID:
        await message.reply_text("ʏᴇᴀʜʜʜ ɪ'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ ᴅᴏ ᴛʜᴀᴛ.")
        return ""

    if await is_user_ban_protected(chat, user_id):
        await message.reply_text("I really wish I could kick this user....")
        return ""

    try:
        await chat.unban_member(user_id) # unban = kick in telegram
        await message.reply_text(f"One Kicked! {member.user.mention}.")
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"ᴋɪᴄᴋᴇᴅ\n"
            f"<b>ᴋɪᴄᴋᴇᴅ ʙʏ:</b> {user.mention}\n"
            f"<b>ᴜsᴇʀ:</b> {member.user.mention}"
        )
        if reason:
            log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {html.escape(reason)}"
        return log
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")
        return ""


@DisableAbleCommandHandler("kickme", admin_ok=False)
async def kickme(client: Client, message: Message):
    user_id = message.from_user.id
    if await is_user_admin(message.chat, user_id):
        await message.reply_text("ɪ ᴡɪsʜ ɪ ᴄᴏᴜʟᴅ... ʙᴜᴛ ʏᴏᴜ'ʀᴇ ᴀɴ ᴀᴅᴍɪɴ.")
        return

    try:
        await message.chat.unban_member(user_id)
        await message.reply_text("*ᴋɪᴄᴋs ʏᴏᴜ ᴏᴜᴛ ᴏғ ᴛʜᴇ ɢʀᴏᴜᴘ*")
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")


@pbot.on_message(filters.command("unban") & filters.group)
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
async def unban(client: Client, message: Message) -> str:
    chat = message.chat
    user = message.from_user
    user_id, reason = await extract_user_and_text(message, message.command[1:])

    if not user_id:
        await message.reply_text("ɪ ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ.")
        return ""

    try:
        member = await client.get_users(user_id)
    except RPCError:
        await message.reply_text("ɪ ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
        return ""

    if user_id == BOT_ID:
        await message.reply_text("ʜᴏᴡ ᴡᴏᴜʟᴅ ɪ ᴜɴʙᴀɴ ᴍʏsᴇʟғ?")
        return ""


    try:
        await chat.unban_member(user_id)
        await message.reply_text("Yep, this user can join!")
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"ᴜɴʙᴀɴɴᴇᴅ\n"
            f"<b>ᴜɴʙᴀɴɴᴇᴅ ʙʏ:</b> {user.mention}\n"
            f"<b>ᴜsᴇʀ:</b> {member.mention}"
        )
        if reason:
            log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {html.escape(reason)}"
        return log
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")
        return ""


@pbot.on_message(filters.command("roar") & filters.group)
@connection_status
@bot_admin
@can_restrict
@gloggable
async def selfunban(client: Client, message: Message) -> str:
    user = message.from_user
    if user.id not in DRAGONS and user.id not in TIGERS:
        return ""

    if len(message.command) < 2:
        await message.reply_text("ɢɪᴠᴇ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ.")
        return ""

    try:
        chat_id = int(message.command[1])
        chat = await client.get_chat(chat_id)
    except Exception:
        await message.reply_text("ɪ ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴄʜᴀᴛ.")
        return ""

    try:
        await chat.unban_member(user.id)
        await message.reply_text("ʏᴇᴘ, ɪ ʜᴀᴠᴇ ᴜɴʙᴀɴɴᴇᴅ ʏᴏᴜ.")
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"ᴜɴʙᴀɴɴᴇᴅ\n"
            f"<b>ᴜɴʙᴀɴɴᴇᴅ ʙʏ:</b> {user.mention}\n"
            f"<b>ᴜsᴇʀ:</b> {user.mention}"
        )
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")
        return ""


__mod_name__ = "Ban"
__help__ = """
 ❍ /kickme: Kicks the user who issued the command

*Admins only:*
 ❍ /ban <userhandle>: Bans a user. (via handle, or reply)
 ❍ /sban <userhandle>: Silently ban a user.
 ❍ /tban <userhandle> x(m/h/d): Bans a user for `x` time.
 ❍ /unban <userhandle>: Unbans a user.
 ❍ /kick <userhandle>: Kicks a user out of the group.
"""
