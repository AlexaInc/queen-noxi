import asyncio
import time
import datetime
import logging
from pyrogram import filters, Client, enums
from pyrogram.types import Message
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    UserIsBlocked,
    PeerIdInvalid,
)

from QueenNoxi import pbot as QueenNoxi
from QueenNoxi import DEV_USERS, OWNER_ID, LOGGER
from QueenNoxi.modules.no_sql import (
    get_served_chats,
    get_served_users,
    remove_served_chat,
    remove_served_users
)

USERS_GROUP = 4
CHAT_GROUP = 5

async def get_user_id(username):
    if not username:
        return None
    if len(username) <= 5 and not str(username).isdigit():
        return None

    if str(username).startswith("@"):
        username = username[1:]

    try:
        user = await QueenNoxi.get_users(username)
        return user.id
    except Exception as e:
        LOGGER.error(f"Error fetching user {username}: {e}")
        return None


@QueenNoxi.on_message(filters.command(["bchat", "broadcastgroups"]) & filters.user(OWNER_ID) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    all_chats = get_served_chats() or []
    await bot.send_message(
        OWNER_ID,
        f"{m.from_user.mention} or {m.from_user.id} Is started the Broadcast......",
    )
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text(f"broadcasting ..")
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_chats = len(all_chats)

    for chat in all_chats:
        sts = await send_chat(chat["chat_id"], broadcast_msg)

        if sts == 200:
            success += 1
        else:
            failed += 1
        done += 1
        if not done % 20:
            await sts_msg.edit(
                f"Broadcast In Progress: \nTotal chats  {total_chats} \nCompleted: {done} / {total_chats}\nSuccess: {success}\nFailed: {failed}"
            )
    
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(
        f"Broadcast Completed: \nCompleted In {completed_in}.\n\nTotal chats {total_chats}\nCompleted: {done} / {total_chats}\nSuccess: {success}\nFailed: {failed}"
    )


async def send_chat(chat_id, message):
    try:
        await message.forward(chat_id=int(chat_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_chat(chat_id, message)
    except InputUserDeactivated:
        remove_served_chat(chat_id)
        LOGGER.info(f"{chat_id} : Deactivated")
        return 400
    except UserIsBlocked:
        remove_served_chat(chat_id)
        LOGGER.info(f"{chat_id} : Blocked The Bot")
        return 400
    except PeerIdInvalid:
        remove_served_chat(chat_id)
        LOGGER.info(f"{chat_id} : User Id Invalid")
        return 400
    except Exception as e:
        remove_served_chat(chat_id)
        LOGGER.error(f"{chat_id} : {e}")
        return 500


@QueenNoxi.on_message(filters.command(["buser", "broadcastusers"]) & filters.user(OWNER_ID) & filters.reply)
async def broadcast_users_handler(bot: Client, m: Message):
    all_users = get_served_users() or []
    await bot.send_message(
        OWNER_ID,
        f"{m.from_user.mention} or {m.from_user.id} Is started the Broadcast......",
    )
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text(f"broadcasting ..")
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = len(all_users)

    for user in all_users:
        sts = await send_msg(user["user_id"], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
        done += 1
        if not done % 20:
            await sts_msg.edit(
                f"Broadcast In Progress: \nTotal Users {total_users} \nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}"
            )
            
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(
        f"Broadcast Completed: \nCompleted In {completed_in}.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}"
    )


async def send_msg(user_id, message):
    try:
        await message.forward(user_id)
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_msg(user_id, message)
    except InputUserDeactivated:
        remove_served_users(user_id)
        LOGGER.info(f"{user_id} : Deactivated")
        return 400
    except UserIsBlocked:
        remove_served_users(user_id)
        LOGGER.info(f"{user_id} : Blocked The Bot")
        return 400
    except PeerIdInvalid:
        remove_served_users(user_id)
        LOGGER.info(f"{user_id} : User Id Invalid")
        return 400
    except Exception as e:
        LOGGER.error(f"{user_id} : {e}")
        return 500


def __stats__():
    return f"• {len(get_served_users())} ᴜsᴇʀs, ᴀᴄʀᴏss {len(get_served_chats())} ᴄʜᴀᴛs"


