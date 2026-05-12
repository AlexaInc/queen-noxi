import html
from pyrogram import filters, Client, enums
from pyrogram.types import Message

import QueenNoxi.modules.sql.blacklistusers_sql as sql
from QueenNoxi import DEMONS, DEV_USERS, DRAGONS, OWNER_ID, TIGERS, WOLVES, pbot
from QueenNoxi.modules.helper_funcs.chat_status import dev_plus
from QueenNoxi.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from QueenNoxi.modules.log_channel import gloggable

BLACKLISTWHITELIST = [OWNER_ID] + DEV_USERS + DRAGONS + WOLVES + DEMONS

@pbot.on_message(filters.command("ignore"))
@dev_plus
@gloggable
async def bl_user(client: Client, message: Message) -> str:
    user_id, reason = await extract_user_and_text(message, message.command[1:])

    if not user_id:
        await message.reply_text("I doubt that's a user.")
        return ""

    if user_id == (await client.get_me()).id:
        await message.reply_text("How am I supposed to do my work if I am ignoring myself?")
        return ""

    if user_id in BLACKLISTWHITELIST:
        await message.reply_text("No!\nNoticing Disasters is my job.")
        return ""

    try:
        target_user = await client.get_users(user_id)
    except Exception:
        await message.reply_text("I can't seem to find this user.")
        return ""

    sql.blacklist_user(user_id, reason)
    await message.reply_text("I shall ignore the existence of this user!")
    
    log_message = (
        f"#BLACKLIST\n"
        f"**Admin:** {message.from_user.mention}\n"
        f"**User:** {target_user.mention}"
    )
    if reason:
        log_message += f"\n**Reason:** {reason}"

    return log_message

@pbot.on_message(filters.command("notice"))
@dev_plus
@gloggable
async def unbl_user(client: Client, message: Message) -> str:
    user_id = await extract_user(message, message.command[1:])

    if not user_id:
        await message.reply_text("I doubt that's a user.")
        return ""

    if user_id == (await client.get_me()).id:
        await message.reply_text("I always notice myself.")
        return ""

    try:
        target_user = await client.get_users(user_id)
    except Exception:
        await message.reply_text("I can't seem to find this user.")
        return ""

    if sql.is_user_blacklisted(user_id):
        sql.unblacklist_user(user_id)
        await message.reply_text("*notices user*")
        log_message = (
            f"#UNBLACKLIST\n"
            f"**Admin:** {message.from_user.mention}\n"
            f"**User:** {target_user.mention}"
        )
        return log_message
    else:
        await message.reply_text("I am not ignoring them at all though!")
        return ""

@pbot.on_message(filters.command("ignoredlist"))
@dev_plus
async def bl_users(client: Client, message: Message):
    users = []
    for each_user in sql.get_all_blacklisted():
        try:
            user = await client.get_users(each_user)
            reason = sql.get_reason(each_user)
            if reason:
                users.append(f"• {user.mention} :- {reason}")
            else:
                users.append(f"• {user.mention}")
        except:
            users.append(f"• `{each_user}` (Not found)")

    message_text = "**Blacklisted Users**\n"
    if not users:
        message_text += "None is being ignored as of yet."
    else:
        message_text += "\n".join(users)

    await message.reply_text(message_text)

def __user_info__(user_id):
    is_blacklisted = sql.is_user_blacklisted(user_id)
    text = "Blacklisted: **{}**"
    if user_id in [777000, 1087968824]:
        return ""
    if user_id == pbot.me.id:
        return ""
    if int(user_id) in DRAGONS + TIGERS + WOLVES:
        return ""
    if is_blacklisted:
        text = text.format("Yes")
        reason = sql.get_reason(user_id)
        if reason:
            text += f"\nReason: `{reason}`"
    else:
        text = text.format("No")
    return text

__mod_name__ = "Ignore"
__help__ = """
ᴛʜɪs ᴍᴏᴅᴜʟᴇ ᴀʟʟᴏᴡs ᴅᴇᴠs ᴛᴏ ɪɢɴᴏʀᴇ sᴘᴀᴍᴍᴇʀs ɢʟᴏʙᴀʟʟʏ.

 ❍ /ignore <ᴜsᴇʀ>: sᴛᴏᴘ ʀᴇsᴘᴏɴᴅɪɴɢ ᴛᴏ ᴛʜɪs ᴜsᴇʀ
 ❍ /notice <ᴜsᴇʀ>: sᴛᴀʀᴛ ʀᴇsᴘᴏɴᴅɪɴɢ ᴛᴏ ᴛʜɪs ᴜsᴇʀ
 ❍ /ignoredlist: ʟɪsᴛ ᴀʟʟ ɪɢɴᴏʀᴇᴅ ᴜsᴇʀs
"""
