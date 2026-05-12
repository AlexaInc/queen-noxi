from datetime import datetime
from functools import wraps

from pyrogram import filters, Client, enums
from pyrogram.types import Message

from QueenNoxi import EVENT_LOGS, LOGGER, pbot
from QueenNoxi.modules.helper_funcs.chat_status import user_admin
from QueenNoxi.modules.sql import log_channel_sql as sql


def loggable(func):
    @wraps(func)
    async def log_action(client: Client, message, *args, **kwargs):
        result = await func(client, message, *args, **kwargs)
        is_cb = hasattr(message, "data") and hasattr(message, "message")
        chat = message.message.chat if is_cb and message.message else message.chat
        
        if result:
            datetime_fmt = "%H:%M - %d-%m-%Y"
            result += f"\n<b>Event Stamp</b>: <code>{datetime.utcnow().strftime(datetime_fmt)}</code>"

            if chat.type == enums.ChatType.SUPERGROUP and chat.username:
                result += f'\n<b>Link:</b> <a href="https://t.me/{chat.username}/{message.id}">click here</a>'
            
            log_chat = sql.get_chat_log_channel(chat.id)
            if log_chat:
                await send_log(client, int(log_chat), chat.id, result)

        return result

    return log_action


def gloggable(func):
    @wraps(func)
    async def glog_action(client: Client, message, *args, **kwargs):
        result = await func(client, message, *args, **kwargs)
        is_cb = hasattr(message, "data") and hasattr(message, "message")
        chat = message.message.chat if is_cb and message.message else message.chat
        
        if result:
            datetime_fmt = "%H:%M - %d-%m-%Y"
            result += f"\n<b>Event Stamp</b>: <code>{datetime.utcnow().strftime(datetime_fmt)}</code>"

            if chat.type == enums.ChatType.SUPERGROUP and chat.username:
                result += f'\n<b>Link:</b> <a href="https://t.me/{chat.username}/{message.id}">click here</a>'
            
            log_chat = EVENT_LOGS
            if log_chat:
                await send_log(client, int(log_chat), chat.id, result)

        return result

    return glog_action


async def send_log(client: Client, log_chat_id: int, orig_chat_id: int, result: str):
    try:
        # Attempt to resolve the peer first to avoid CHANNEL_INVALID
        try:
            await client.get_chat(log_chat_id)
        except Exception:
            pass
            
        await client.send_message(
            log_chat_id,
            result,
            disable_web_page_preview=True,
        )
    except Exception as excp:
        if "CHAT_WRITE_FORBIDDEN" in str(excp) or "CHANNEL_INVALID" in str(excp):
            LOGGER.warning(f"Logging disabled for {orig_chat_id} due to: {excp}")
            sql.stop_chat_logging(orig_chat_id)
        else:
            LOGGER.warning(f"Could not send log: {excp}")


@pbot.on_message(filters.command("logchannel") & filters.group)
@user_admin
async def logging(client: Client, message: Message):
    chat = message.chat
    log_channel = sql.get_chat_log_channel(chat.id)
    if log_channel:
        try:
            log_channel_info = await client.get_chat(int(log_channel))
            await message.reply_text(
                f"This group has all its logs sent to: {log_channel_info.title} (`{log_channel}`)"
            )
        except Exception:
            await message.reply_text(f"This group has its logs sent to channel: `{log_channel}`")
    else:
        await message.reply_text("No log channel has been set for this group!")


@pbot.on_message(filters.command("setlog") & filters.group)
@user_admin
async def setlog(client: Client, message: Message):
    if message.forward_from_chat and message.forward_from_chat.type == enums.ChatType.CHANNEL:
        sql.set_chat_log_channel(message.chat.id, message.forward_from_chat.id)
        try:
            await message.delete()
        except:
            pass

        try:
            await client.send_message(
                message.forward_from_chat.id,
                f"This channel has been set as the log channel for {message.chat.title}.",
            )
        except Exception as e:
            LOGGER.warning(f"Error in setlog: {e}")

        await message.reply_text("Successfully set log channel!")
    else:
        await message.reply_text(
            "The steps to set a log channel are:\n"
            " - Add bot to the desired channel as an admin\n"
            " - Send /setlog to the channel\n"
            " - Forward the /setlog to the group\n"
        )


@pbot.on_message(filters.command("unsetlog") & filters.group)
@user_admin
async def unsetlog(client: Client, message: Message):
    log_channel = sql.stop_chat_logging(message.chat.id)
    if log_channel:
        try:
            await client.send_message(int(log_channel), f"Channel has been unlinked from {message.chat.title}")
        except:
            pass
        await message.reply_text("Log channel has been unset.")
    else:
        await message.reply_text("No log channel has been set yet!")


def __stats__():
    return f"• {sql.num_logchannels()} ʟᴏɢ ᴄʜᴀɴɴᴇʟs sᴇᴛ."


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


async def __chat_settings__(chat_id, user_id):
    log_channel = sql.get_chat_log_channel(chat_id)
    if log_channel:
        try:
            log_channel_info = await pbot.get_chat(int(log_channel))
            return f"This group has all its logs sent to: {log_channel_info.title} (`{log_channel}`)"
        except:
            return f"This group has its logs sent to channel ID: `{log_channel}`"
    return "No log channel is set for this group!"


__mod_name__ = "Logs"
__help__ = """
*Admins only:*
 ❍ /logchannel: Get log channel info
 ❍ /setlog: Set the log channel.
 ❍ /unsetlog: Unset the log channel.

Setting the log channel is done by:
1. Adding the bot to the desired channel as an admin.
2. Sending /setlog in the channel.
3. Forwarding that /setlog message to the group.
"""
