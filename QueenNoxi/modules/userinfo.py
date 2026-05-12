import html
import os
import re
import asyncio
from pyrogram import filters, Client, enums
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from pyrogram.errors import RPCError
from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import ChannelParticipantsAdmins

import QueenNoxi.modules.sql.userinfo_sql as sql
from QueenNoxi import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    INFOPIC,
    OWNER_ID,
    OWNER_IDS,
    TIGERS,
    WOLVES,
    pbot,
    telethn,
    BOT_NAME,
    BOT_USERNAME,
    BOT_ID
)
from QueenNoxi.modules.disable import DisableAbleCommandHandler
from QueenNoxi.modules.helper_funcs.chat_status import sudo_plus
from QueenNoxi.modules.helper_funcs.extraction import extract_user
from QueenNoxi.modules.sql.global_bans_sql import is_user_gbanned
from QueenNoxi.modules.sql.users_sql import get_user_num_chats

def no_by_per(totalhp, percentage):
    return totalhp * percentage / 100

def get_percentage(totalhp, earnedhp):
    matched_less = totalhp - earnedhp
    per_of_totalhp = 100 - matched_less * 100.0 / totalhp
    return str(int(per_of_totalhp))

async def hpmanager(user):
    total_hp = (get_user_num_chats(user.id) + 10) * 10
    new_hp = total_hp
    if not await is_user_gbanned(user.id):
        if not user.username:
            new_hp -= no_by_per(total_hp, 25)
        try:
            photos = [p async for p in pbot.get_chat_photos(user.id)]
            if not photos:
                new_hp -= no_by_per(total_hp, 25)
        except:
            new_hp -= no_by_per(total_hp, 25)
        if not sql.get_user_me_info(user.id):
            new_hp -= no_by_per(total_hp, 20)
        if not sql.get_user_bio(user.id):
            new_hp -= no_by_per(total_hp, 10)
    else:
        new_hp = no_by_per(total_hp, 5)
    return {
        "earnedhp": int(new_hp),
        "totalhp": int(total_hp),
        "percentage": get_percentage(total_hp, new_hp),
    }

def make_bar(per):
    done = min(round(int(per) / 10), 10)
    return "■" * done + "□" * (10 - done)

@pbot.on_message(filters.command("id"))
async def get_id(client: Client, message: Message):
    chat = message.chat
    if len(message.command) > 1:
        user_id = await extract_user(message, message.command[1:])
        if user_id:
            user = await client.get_users(user_id)
            await message.reply_text(f"{user.first_name}'s ID is `{user.id}`.")
        else:
            await message.reply_text("I can't find that user.")
    else:
        if chat.type == enums.ChatType.PRIVATE:
            await message.reply_text(f"Your ID is `{message.from_user.id}`.")
        else:
            await message.reply_text(f"This group's ID is `{chat.id}`.")

@pbot.on_message(filters.command("info"))
async def info(client: Client, message: Message):
    user_id = await extract_user(message, message.command[1:]) or message.from_user.id
    user = await client.get_users(user_id)
    chat = message.chat

    text = (
        f"✦ **User Info** ✦\n"
        f"➻ **ID:** `{user.id}`\n"
        f"➻ **First Name:** {html.escape(user.first_name)}\n"
    )
    if user.last_name:
        text += f"➻ **Last Name:** {html.escape(user.last_name)}\n"
    if user.username:
        text += f"➻ **Username:** @{user.username}\n"
    
    text += f"➻ **Mention:** {user.mention}\n"

    # Presence in group
    if chat.type != enums.ChatType.PRIVATE:
        try:
            member = await chat.get_member(user.id)
            text += f"➻ **Status:** `{member.status}`\n"
        except:
            pass

    userhp = await hpmanager(user)
    text += f"\n**Health:** `{userhp['earnedhp']}/{userhp['totalhp']}`\n"
    text += f"[{make_bar(userhp['percentage'])} {userhp['percentage']}%]\n"

    # Disaster Levels
    if user.id == OWNER_ID:
        text += "\nThis user is **GOD**.\n"
    elif user.id in DEV_USERS:
        text += "\nThis user is a **Developer**.\n"
    elif user.id in DRAGONS:
        text += "\nThis user is a **Dragon**.\n"

    if INFOPIC:
        try:
            photo = [p async for p in client.get_chat_photos(user.id, limit=1)][0]
            await message.reply_photo(
                photo.file_id,
                caption=text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Health Guide", url="https://t.me/queennoxibotzone/90")],
                    [InlineKeyboardButton("Add Me", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]
                ])
            )
        except:
            await message.reply_text(text)
    else:
        await message.reply_text(text)

@pbot.on_message(filters.command("me"))
async def about_me(client: Client, message: Message):
    user_id = await extract_user(message, message.command[1:]) or message.from_user.id
    user = await client.get_users(user_id)
    info = sql.get_user_me_info(user.id)
    if info:
        await message.reply_text(f"**{user.first_name}**:\n{info}")
    else:
        await message.reply_text("No info set yet!")

@pbot.on_message(filters.command("setme"))
async def set_about_me(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /setme <info>")
        return
    text = message.text.split(None, 1)[1]
    sql.set_user_me_info(message.from_user.id, text)
    await message.reply_text("Info updated!")

@pbot.on_message(filters.command("bio"))
async def about_bio(client: Client, message: Message):
    user_id = await extract_user(message, message.command[1:]) or message.from_user.id
    user = await client.get_users(user_id)
    bio = sql.get_user_bio(user.id)
    if bio:
        await message.reply_text(f"**{user.first_name}**'s Bio:\n{bio}")
    else:
        await message.reply_text("No bio set yet!")

@pbot.on_message(filters.command("setbio"))
async def set_about_bio(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Reply to someone to set their bio!")
        return
    if len(message.command) < 2:
        await message.reply_text("Usage: /setbio <text>")
        return
    
    target_user = message.reply_to_message.from_user
    if target_user.id == message.from_user.id:
        await message.reply_text("You can't set your own bio!")
        return
    
    text = message.text.split(None, 1)[1]
    sql.set_user_bio(target_user.id, text)
    await message.reply_text(f"Updated {target_user.first_name}'s bio!")

__mod_name__ = "Info"
__help__ = """
• `/id`: Get user/chat ID
• `/info`: Get user info
• `/me`: Get user-set info
• `/setme`: Set your own info
• `/bio`: Get user bio (set by others)
• `/setbio`: Set another user's bio
"""
