import html
from pyrogram import filters, Client, enums
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
    ChatPermissions,
)
from pyrogram.errors import RPCError, BadRequest

import QueenNoxi.modules.sql.blsticker_sql as sql
from QueenNoxi import LOGGER, pbot
from QueenNoxi.modules.connection import connected
from QueenNoxi.modules.disable import DisableAbleCommandHandler
from QueenNoxi.modules.helper_funcs.chat_status import user_admin, user_not_admin
from QueenNoxi.modules.helper_funcs.string_handling import extract_time
from QueenNoxi.modules.log_channel import loggable
from QueenNoxi.modules.warns import warn

@pbot.on_message(filters.command("blsticker") & filters.group)
@user_admin
async def blackliststicker(client: Client, message: Message):
    chat_id = await connected(client, message, message.from_user.id, need_admin=False)
    if not chat_id:
        chat_id = message.chat.id
        chat_name = message.chat.title
    else:
        try:
            chat = await client.get_chat(chat_id)
            chat_name = chat.title
        except:
            chat_name = f"Chat {chat_id}"

    sticker_list = f"**List blacklisted stickers in {html.escape(chat_name)}:**\n"
    all_stickerlist = sql.get_chat_stickers(chat_id)

    if not all_stickerlist:
        await message.reply_text(f"There are no blacklisted stickers in **{html.escape(chat_name)}**!")
        return

    for trigger in all_stickerlist:
        sticker_list += f" - `{html.escape(trigger)}`\n"

    await message.reply_text(sticker_list)

@pbot.on_message(filters.command("addblsticker") & filters.group)
@user_admin
async def add_blackliststicker(client: Client, message: Message):
    chat_id = await connected(client, message, message.from_user.id)
    if not chat_id:
        chat_id = message.chat.id
        chat_name = message.chat.title
    else:
        chat = await client.get_chat(chat_id)
        chat_name = chat.title

    args = message.command[1:]
    if args:
        text = " ".join(args).replace("https://t.me/addstickers/", "")
        to_blacklist = list({trigger.strip() for trigger in text.split("\n") if trigger.strip()})

        added = 0
        for trigger in to_blacklist:
            sql.add_to_stickers(chat_id, trigger.lower())
            added += 1

        if added > 0:
            await message.reply_text(f"Added {added} stickers to blacklist in **{html.escape(chat_name)}**!")
    elif message.reply_to_message and message.reply_to_message.sticker:
        trigger = message.reply_to_message.sticker.set_name
        if not trigger:
            await message.reply_text("Sticker is invalid!")
            return
        sql.add_to_stickers(chat_id, trigger.lower())
        await message.reply_text(f"Sticker `{trigger}` added to blacklist in **{html.escape(chat_name)}**!")
    else:
        await message.reply_text("Please provide a sticker set name or reply to a sticker.")

@pbot.on_message(filters.command(["unblsticker", "rmblsticker"]) & filters.group)
@user_admin
async def unblackliststicker(client: Client, message: Message):
    chat_id = await connected(client, message, message.from_user.id)
    if not chat_id:
        chat_id = message.chat.id
        chat_name = message.chat.title
    else:
        chat = await client.get_chat(chat_id)
        chat_name = chat.title

    args = message.command[1:]
    if args:
        text = " ".join(args).replace("https://t.me/addstickers/", "")
        to_unblacklist = list({trigger.strip() for trigger in text.split("\n") if trigger.strip()})

        successful = 0
        for trigger in to_unblacklist:
            if sql.rm_from_stickers(chat_id, trigger.lower()):
                successful += 1

        if successful > 0:
            await message.reply_text(f"Removed {successful} stickers from blacklist in **{html.escape(chat_name)}**!")
        else:
            await message.reply_text("None of these stickers were blacklisted.")
    elif message.reply_to_message and message.reply_to_message.sticker:
        trigger = message.reply_to_message.sticker.set_name
        if not trigger:
            await message.reply_text("Sticker is invalid!")
            return
        if sql.rm_from_stickers(chat_id, trigger.lower()):
            await message.reply_text(f"Sticker `{trigger}` removed from blacklist in **{html.escape(chat_name)}**!")
        else:
            await message.reply_text("This sticker was not blacklisted.")
    else:
        await message.reply_text("Please provide a sticker set name or reply to a sticker.")

@pbot.on_message(filters.command("blstickermode") & filters.group)
@user_admin
@loggable
async def blacklist_mode(client: Client, message: Message) -> str:
    chat_id = await connected(client, message, message.from_user.id)
    if not chat_id:
        chat_id = message.chat.id
        chat_name = message.chat.title
    else:
        chat = await client.get_chat(chat_id)
        chat_name = chat.title

    args = message.command[1:]
    if args:
        mode = args[0].lower()
        if mode in ("off", "nothing", "no"):
            sql.set_blacklist_strength(chat_id, 0, "0")
            msg = "Blacklist sticker mode disabled."
        elif mode in ("del", "delete"):
            sql.set_blacklist_strength(chat_id, 1, "0")
            msg = "Blacklist sticker mode set to: DELETE."
        elif mode == "warn":
            sql.set_blacklist_strength(chat_id, 2, "0")
            msg = "Blacklist sticker mode set to: WARN."
        elif mode == "mute":
            sql.set_blacklist_strength(chat_id, 3, "0")
            msg = "Blacklist sticker mode set to: MUTE."
        elif mode == "kick":
            sql.set_blacklist_strength(chat_id, 4, "0")
            msg = "Blacklist sticker mode set to: KICK."
        elif mode == "ban":
            sql.set_blacklist_strength(chat_id, 5, "0")
            msg = "Blacklist sticker mode set to: BAN."
        else:
            await message.reply_text("Invalid mode! Use: off/del/warn/mute/kick/ban")
            return ""

        await message.reply_text(f"{msg} in **{html.escape(chat_name)}**.")
        return f"**{html.escape(chat_name)}:**\n#BLSTICKER_MODE\n**Admin:** {message.from_user.mention}\nMode: {mode}"
    else:
        mode, value = sql.get_blacklist_setting(chat_id)
        modes = ["Off", "Delete", "Warn", "Mute", "Kick", "Ban"]
        await message.reply_text(f"Current blacklist sticker mode: **{modes[mode]}**.")
    return ""

@pbot.on_message(filters.sticker & filters.group, group=11)
@user_not_admin
async def del_blackliststicker(client: Client, message: Message):
    chat_id = message.chat.id
    sticker = message.sticker
    if not sticker or not sticker.set_name:
        return

    mode, value = sql.get_blacklist_setting(chat_id)
    if mode == 0:
        return

    chat_filters = sql.get_chat_stickers(chat_id)
    if sticker.set_name.lower() in [s.lower() for s in chat_filters]:
        try:
            await message.delete()
            if mode == 2: # Warn
                await warn(message.from_user, chat_id, f"Using blacklisted sticker: {sticker.set_name}", message)
            elif mode == 3: # Mute
                await message.chat.restrict_member(message.from_user.id, ChatPermissions(can_send_messages=False))
            elif mode == 4: # Kick
                await message.chat.unban_member(message.from_user.id)
            elif mode == 5: # Ban
                await message.chat.ban_member(message.from_user.id)
        except Exception as e:
            LOGGER.warning(f"Error in del_blackliststicker: {e}")

__mod_name__ = "Sᴛɪᴄᴋᴇʀ"
__help__ = """
ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀ ɪs ᴜsᴇᴅ ᴛᴏ sᴛᴏᴘ ᴄᴇʀᴛᴀɪɴ sᴛɪᴄᴋᴇʀs. ᴡʜᴇɴᴇᴠᴇʀ ᴀ sᴛɪᴄᴋᴇʀ ɪs sᴇɴᴛ, ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪᴍᴍᴇᴅɪᴀᴛᴇʟʏ.

 ❍ /blsticker: sᴇᴇ ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ sᴛɪᴄᴋᴇʀ
 ❍ /addblsticker <sᴛɪᴄᴋᴇʀ ʟɪɴᴋ>: ᴀᴅᴅ sᴛɪᴄᴋᴇʀ ᴛᴏ ʙʟᴀᴄᴋʟɪsᴛ
 ❍ /unblsticker <sᴛɪᴄᴋᴇʀ ʟɪɴᴋ>: ʀᴇᴍᴏᴠᴇ sᴛɪᴄᴋᴇʀ ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ
 ❍ /blstickermode <off/del/warn/mute/kick/ban>: sᴇᴛ ᴅᴇғᴀᴜʟᴛ ᴀᴄᴛɪᴏɴ
"""
