import html
from typing import Optional

from pyrogram import filters, Client, enums
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import RPCError

from QueenNoxi import LOGGER, TIGERS, pbot, BOT_ID
from QueenNoxi.modules.disable import DisableAbleCommandHandler
from QueenNoxi.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    connection_status,
    is_user_admin,
    user_admin,
)
from QueenNoxi.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from QueenNoxi.modules.helper_funcs.string_handling import extract_time
from QueenNoxi.modules.log_channel import loggable


async def check_user(user_id: int, chat) -> Optional[str]:
    if not user_id:
        return "You don't seem to be referring to a user or the ID specified is incorrect.."

    try:
        member = await chat.get_member(user_id)
    except RPCError:
        return "I can't seem to find this user"

    if user_id == BOT_ID:
        return "I'm not gonna MUTE myself, How high are you?"

    if await is_user_admin(chat, user_id) or user_id in TIGERS:
        return "Can't. Find someone else to mute but not this one."

    return None


@pbot.on_message(filters.command("mute") & filters.group)
@connection_status
@bot_admin
@user_admin
@loggable
async def mute(client: Client, message: Message) -> str:
    chat = message.chat
    user = message.from_user
    user_id, reason = await extract_user_and_text(message, message.command[1:])
    reply = await check_user(user_id, chat)

    if reply:
        await message.reply_text(reply)
        return ""

    member = await chat.get_member(user_id)
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#MUTE\n"
        f"<b>Admin:</b> {user.mention}\n"
        f"<b>User:</b> {member.user.mention}"
    )
    if reason:
        log += f"\n<b>Reason:</b> {html.escape(reason)}"

    if member.permissions and member.permissions.can_send_messages:
        try:
            await chat.restrict_member(user_id, ChatPermissions(can_send_messages=False))
            await message.reply_text(f"Muted <b>{html.escape(member.user.first_name)}</b> with no expiration date!")
            return log
        except RPCError as e:
            await message.reply_text(f"Error: {e.MESSAGE}")
    else:
        await message.reply_text("This user is already muted!")

    return ""


@pbot.on_message(filters.command("dmute") & filters.group)
@connection_status
@bot_admin
@user_admin
@loggable
async def dmute(client: Client, message: Message) -> str:
    chat = message.chat
    user = message.from_user
    user_id, reason = await extract_user_and_text(message, message.command[1:])
    
    try:
        await message.delete()
    except:
        pass

    reply = await check_user(user_id, chat)
    if reply:
        await message.reply_text(reply)
        return ""

    member = await chat.get_member(user_id)
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#MUTE\n"
        f"<b>Admin:</b> {user.mention}\n"
        f"<b>User:</b> {member.user.mention}"
    )
    if reason:
        log += f"\n<b>Reason:</b> {html.escape(reason)}"

    if member.permissions and member.permissions.can_send_messages:
        try:
            await chat.restrict_member(user_id, ChatPermissions(can_send_messages=False))
            return log
        except RPCError as e:
            LOGGER.warning(f"Error dmute: {e}")
    return ""


@pbot.on_message(filters.command("unmute") & filters.group)
@connection_status
@bot_admin
@user_admin
@loggable
async def unmute(client: Client, message: Message) -> str:
    chat = message.chat
    user = message.from_user
    user_id = await extract_user(message, message.command[1:])

    if not user_id:
        await message.reply_text("You'll need to either give me a username to unmute, or reply to someone.")
        return ""

    try:
        member = await chat.get_member(user_id)
    except RPCError:
        await message.reply_text("I can't seem to find this user")
        return ""

    if member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.LEFT]:
        await message.reply_text("This user isn't even in the chat!")
        return ""

    if member.permissions and member.permissions.can_send_messages:
        await message.reply_text("This user already has the right to speak.")
        return ""

    try:
        await chat.restrict_member(
            user_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        )
        await message.reply_text(f"I shall allow <b>{html.escape(member.user.first_name)}</b> to text!")
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#UNMUTE\n"
            f"<b>Admin:</b> {user.mention}\n"
            f"<b>User:</b> {member.user.mention}"
        )
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")
    return ""


@pbot.on_message(filters.command(["tmute", "tempmute"]) & filters.group)
@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
async def temp_mute(client: Client, message: Message) -> str:
    chat = message.chat
    user = message.from_user
    user_id, reason = await extract_user_and_text(message, message.command[1:])
    reply = await check_user(user_id, chat)

    if reply:
        await message.reply_text(reply)
        return ""

    member = await chat.get_member(user_id)
    if not reason:
        await message.reply_text("You haven't specified a time to mute this user for!")
        return ""

    split_reason = reason.split(None, 1)
    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    mutetime = await extract_time(message, time_val)

    if not mutetime:
        return ""

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#TEMP MUTED\n"
        f"<b>Admin:</b> {user.mention}\n"
        f"<b>User:</b> {member.user.mention}\n"
        f"<b>Time:</b> {time_val}"
    )
    if reason:
        log += f"\n<b>Reason:</b> {html.escape(reason)}"

    if member.permissions and member.permissions.can_send_messages:
        try:
            await chat.restrict_member(
                user_id,
                ChatPermissions(can_send_messages=False),
                until_date=mutetime
            )
            await message.reply_text(f"Muted <b>{html.escape(member.user.first_name)}</b> for {time_val}!")
            return log
        except RPCError as e:
            await message.reply_text(f"Error: {e.MESSAGE}")
    else:
        await message.reply_text("This user is already muted.")

    return ""


__mod_name__ = "Mute"
__help__ = """
*Admins only:*
 ❍ /mute <userhandle>: Silences a user.
 ❍ /tmute <userhandle> x(m/h/d): Mutes a user for x time.
 ❍ /unmute <userhandle>: Unmutes a user.
 ❍ /dmute <userhandle>: Silences a user and deletes the command.
"""
