import ast
import csv
import json
import os
import re
import time
import uuid
from io import BytesIO

from pyrogram import filters, Client, enums
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
    MessageEntity,
)
from pyrogram.errors import RPCError, Forbidden, BadRequest

import QueenNoxi.modules.sql.feds_sql as sql
from QueenNoxi import (
    DRAGONS,
    EVENT_LOGS,
    LOGGER,
    OWNER_ID,
    SUPPORT_CHAT,
    TIGERS,
    WOLVES,
    pbot,
)
from QueenNoxi.modules.disable import DisableAbleCommandHandler
from QueenNoxi.modules.helper_funcs.chat_status import user_admin, connection_status
from QueenNoxi.modules.helper_funcs.extraction import (
    extract_unt_fedban,
    extract_user,
    extract_user_fban,
)
from QueenNoxi.modules.helper_funcs.string_handling import markdown_parser

FBAN_ERRORS = {
    "USER_ADMIN_INVALID",
    "CHAT_NOT_FOUND",
    "NOT_ENOUGH_RIGHTS_TO_RESTRICT",
    "USER_NOT_PARTICIPANT",
    "PEER_ID_INVALID",
    "GROUP_DEACTIVATED",
    "CHAT_ADMIN_REQUIRED",
    "CHANNEL_PRIVATE",
    "NOT_IN_CHAT",
}

UNFBAN_ERRORS = {
    "USER_ADMIN_INVALID",
    "CHAT_NOT_FOUND",
    "NOT_ENOUGH_RIGHTS_TO_RESTRICT",
    "USER_NOT_PARTICIPANT",
    "CHANNEL_PRIVATE",
    "CHAT_ADMIN_REQUIRED",
}

@pbot.on_message(filters.command("newfed"))
async def new_fed(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    if chat.type != enums.ChatType.PRIVATE:
        await message.reply_text(
            "Federations can only be created by privately messaging me.",
        )
        return
    
    args = message.command[1:]
    if not args:
        await message.reply_text("Please write the name of the federation!")
        return
        
    fed_name = " ".join(args)
    fed_id = str(uuid.uuid4())
    
    x = sql.new_fed(user.id, fed_name, fed_id)
    if not x:
        await message.reply_text(
            f"Can't federate! Please contact @{SUPPORT_CHAT} if the problem persist.",
        )
        return

    await message.reply_text(
        "**You have succeeded in creating a new federation!**\n"
        f"Name: `{fed_name}`\n"
        f"ID: `{fed_id}`\n\n"
        "Use the command below to join the federation:\n"
        f"`/joinfed {fed_id}`"
    )
    try:
        await client.send_message(
            EVENT_LOGS,
            f"New Federation: <b>{fed_name}</b>\nID: <pre>{fed_id}</pre>",
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception as e:
        LOGGER.warning(f"Cannot send a message to EVENT_LOGS: {e}")

@pbot.on_message(filters.command("delfed"))
async def del_fed(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    if chat.type != enums.ChatType.PRIVATE:
        await message.reply_text(
            "Federations can only be deleted in personal chat.",
        )
        return
    
    args = message.command[1:]
    if not args:
        await message.reply_text("Please provide your federation ID.")
        return
    
    fed_id = args[0]
    owner_id = sql.get_fed_info(fed_id).get("owner")
    
    if str(owner_id) != str(user.id):
        await message.reply_text("Only the federation owner can delete this!")
        return
    
    await message.reply_text(
        "Are you sure you want to delete your federation? This action cannot be undone, you will lose your entire ban list, and all your sub-feds will be disconnected.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Delete Federation",
                        callback_data=f"rm_fed_{fed_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Cancel",
                        callback_data="rm_fed_cancel",
                    )
                ],
            ]
        ),
    )

@pbot.on_message(filters.command("fedname"))
async def rename_fed(client: Client, message: Message):
    user = message.from_user
    args = message.command[1:]
    if not args:
        await message.reply_text("Please provide a name for the federation.")
        return
        
    fed_id = sql.get_fed_id(message.chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
    
    info = sql.get_fed_info(fed_id)
    if str(info["owner"]) != str(user.id):
        await message.reply_text("Only the federation owner can rename this!")
        return

    new_name = " ".join(args)
    sql.rename_fed(fed_id, new_name)
    await message.reply_text(f"Successfully renamed your federation to {new_name}!")

@pbot.on_message(filters.command("joinfed"))
async def join_fed(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    
    if chat.type == enums.ChatType.PRIVATE:
        await message.reply_text("This command can only be used in groups.")
        return
        
    member = await chat.get_member(user.id)
    if member.status != enums.ChatMemberStatus.OWNER and user.id not in DRAGONS:
        await message.reply_text("Only group owners can join a federation!")
        return
        
    args = message.command[1:]
    if not args:
        await message.reply_text("Please provide a federation ID.")
        return
        
    fed_id = args[0]
    getfed = sql.get_fed_info(fed_id)
    if not getfed:
        await message.reply_text("Invalid federation ID!")
        return
        
    res = sql.chat_join_fed(fed_id, chat.title, chat.id)
    if res:
        await message.reply_text(f"Successfully joined the federation {getfed['fname']}!")
    else:
        await message.reply_text("This group is already part of a federation!")

@pbot.on_message(filters.command("leavefed"))
async def leave_fed(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    
    if chat.type == enums.ChatType.PRIVATE:
        await message.reply_text("This command can only be used in groups.")
        return
        
    member = await chat.get_member(user.id)
    if member.status != enums.ChatMemberStatus.OWNER and user.id not in DRAGONS:
        await message.reply_text("Only group owners can leave a federation!")
        return
        
    fed_id = sql.get_fed_id(chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
        
    res = sql.chat_leave_fed(chat.id)
    if res:
        await message.reply_text("Successfully left the federation!")
    else:
        await message.reply_text("Failed to leave the federation.")

@pbot.on_message(filters.command("fprom"))
async def user_join_fed(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    fed_id = sql.get_fed_id(chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
    
    info = sql.get_fed_info(fed_id)
    if str(info["owner"]) != str(user.id):
        await message.reply_text("Only the federation owner can promote people!")
        return
        
    user_id = await extract_user(message, message.command[1:])
    if not user_id:
        await message.reply_text("You need to specify a user to promote.")
        return
        
    res = sql.user_join_fed(fed_id, user_id)
    if res:
        await message.reply_text("Successfully promoted user to federation admin!")
    else:
        await message.reply_text("User is already a federation admin!")

@pbot.on_message(filters.command("fdem"))
async def user_demote_fed(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    fed_id = sql.get_fed_id(chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
    
    info = sql.get_fed_info(fed_id)
    if str(info["owner"]) != str(user.id):
        await message.reply_text("Only the federation owner can demote people!")
        return
        
    user_id = await extract_user(message, message.command[1:])
    if not user_id:
        await message.reply_text("You need to specify a user to demote.")
        return
        
    if str(info["owner"]) == str(user_id):
        await message.reply_text("You cannot demote the owner!")
        return

    res = sql.user_demote_fed(fed_id, user_id)
    if res:
        await message.reply_text("Successfully demoted user from federation admin!")
    else:
        await message.reply_text("User is not a federation admin!")

@pbot.on_message(filters.command("fedinfo"))
async def fed_info(client: Client, message: Message):
    args = message.command[1:]
    if not args:
        fed_id = sql.get_fed_id(message.chat.id)
        if not fed_id:
            await message.reply_text("Please provide a federation ID or use this in a federated group.")
            return
    else:
        fed_id = args[0]
        
    info = sql.get_fed_info(fed_id)
    if not info:
        await message.reply_text("Invalid federation ID!")
        return
        
    numban = sql.get_all_fban_users(fed_id)
    numchat = sql.get_all_fed_chats(fed_id)
    
    text = (
        f"**Federation Information:**\n"
        f"**Name:** {info['fname']}\n"
        f"**ID:** `{fed_id}`\n"
        f"**Owner:** {info['owner']}\n"
        f"**Admins:** {len(sql.all_fed_admins(fed_id))}\n"
        f"**Banned Users:** {len(numban)}\n"
        f"**Connected Chats:** {len(numchat)}"
    )
    await message.reply_text(text)

@pbot.on_message(filters.command("fedadmins"))
async def fed_admin(client: Client, message: Message):
    fed_id = sql.get_fed_id(message.chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
    
    info = sql.get_fed_info(fed_id)
    admins = sql.all_fed_admins(fed_id)
    
    text = f"**Admins in {info['fname']}:**\n"
    text += f"- [{info['owner']}](tg://user?id={info['owner']}) (Owner)\n"
    for admin in admins:
        text += f"- [{admin['user_id']}](tg://user?id={admin['user_id']})\n"
        
    await message.reply_text(text)

@pbot.on_message(filters.command("fban") & filters.group)
@DisableAbleCommandHandler("fban")
async def fed_ban(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    args = message.command[1:]

    fed_id = sql.get_fed_id(chat.id)
    if not fed_id:
        await message.reply_text("This group is not a part of any federation!")
        return

    info = sql.get_fed_info(fed_id)
    getfednotif = sql.user_feds_report(info["owner"])

    # Check if user is fed admin
    if not sql.is_user_fed_admin(fed_id, user.id):
        await message.reply_text("Only federation admins can do this!")
        return

    user_id, reason = await extract_unt_fedban(message, args)
    if not user_id:
        await message.reply_text("You don't seem to be referring to a user")
        return

    me = await client.get_me()
    if user_id == me.id:
        await message.reply_text("I cannot fban myself!")
        return

    if sql.is_user_fed_owner(fed_id, user_id):
        await message.reply_text("He is the federation owner!")
        return

    if sql.is_user_fed_admin(fed_id, user_id):
        await message.reply_text("He is a federation admin!")
        return

    if user_id == OWNER_ID or user_id in DRAGONS or user_id in TIGERS or user_id in WOLVES:
        await message.reply_text("This user cannot be fed banned!")
        return

    try:
        user_chat = await client.get_users(user_id)
        fban_user_id = user_chat.id
        fban_user_name = user_chat.first_name
        fban_user_lname = user_chat.last_name
        fban_user_uname = user_chat.username
    except Exception:
        fban_user_id = int(user_id)
        fban_user_name = f"user({user_id})"
        fban_user_lname = None
        fban_user_uname = None

    user_target = f"[{fban_user_name}](tg://user?id={fban_user_id})"
    
    fban, fbanreason, fbantime = sql.get_fban_user(fed_id, fban_user_id)
    if fban:
        sql.un_fban_user(fed_id, fban_user_id)
        
    x = sql.fban_user(
        fed_id,
        fban_user_id,
        fban_user_name,
        fban_user_lname,
        fban_user_uname,
        reason or "No reason provided",
        int(time.time()),
    )
    if not x:
        await message.reply_text("Failed to ban from the federation!")
        return

    reply_text = (
        "**New FedBan**\n"
        f"**Federation:** {info['fname']}\n"
        f"**Federation Admin:** {user.mention}\n"
        f"**User:** {user_target}\n"
        f"**User ID:** `{fban_user_id}`\n"
        f"**Reason:** {reason or 'No reason provided'}"
    )
    await message.reply_text(reply_text)

    get_fedlog = sql.get_fed_log(fed_id)
    if get_fedlog:
        try:
            await client.send_message(get_fedlog, reply_text)
        except Exception:
            pass

    fed_chats = sql.all_fed_chats(fed_id)
    for fchat in fed_chats:
        try:
            await client.ban_chat_member(fchat, fban_user_id)
        except Exception:
            pass

@pbot.on_message(filters.command("unfban") & filters.group)
@DisableAbleCommandHandler("unfban")
async def unfban(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    args = message.command[1:]

    fed_id = sql.get_fed_id(chat.id)
    if not fed_id:
        await message.reply_text("This group is not a part of any federation!")
        return

    if not sql.is_user_fed_admin(fed_id, user.id):
        await message.reply_text("Only federation admins can do this!")
        return

    user_id = await extract_user(message, args)
    if not user_id:
        await message.reply_text("You don't seem to be referring to a user")
        return

    fban, fbanreason, fbantime = sql.get_fban_user(fed_id, user_id)
    if not fban:
        await message.reply_text("This user is not fedanned!")
        return

    sql.un_fban_user(fed_id, user_id)
    await message.reply_text(f"Successfully un-fedbanned user.")

    fed_chats = sql.all_fed_chats(fed_id)
    for fchat in fed_chats:
        try:
            await client.unban_chat_member(fchat, user_id)
        except Exception:
            pass

@pbot.on_message(filters.command("setfrules"))
async def set_frules(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    fed_id = sql.get_fed_id(chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
    
    info = sql.get_fed_info(fed_id)
    if str(info["owner"]) != str(user.id):
        await message.reply_text("Only the federation owner can set rules!")
        return

    rules = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    sql.set_frules(fed_id, rules)
    await message.reply_text("Successfully set federation rules!")

@pbot.on_message(filters.command("frules"))
async def get_frules(client: Client, message: Message):
    fed_id = sql.get_fed_id(message.chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
    
    rules = sql.get_frules(fed_id)
    if not rules:
        await message.reply_text("This federation has no rules.")
        return
    
    await message.reply_text(f"**Federation Rules:**\n\n{rules}")

@pbot.on_message(filters.command("fbroadcast"))
async def fed_broadcast(client: Client, message: Message):
    user = message.from_user
    fed_id = sql.get_fed_id(message.chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
    
    info = sql.get_fed_info(fed_id)
    if str(info["owner"]) != str(user.id):
        await message.reply_text("Only the federation owner can broadcast!")
        return
        
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    if not text:
        await message.reply_text("What do you want to broadcast?")
        return
        
    chats = sql.all_fed_chats(fed_id)
    for chat_id in chats:
        try:
            await client.send_message(chat_id, text)
        except Exception:
            pass
    await message.reply_text("Broadcast sent!")

@pbot.on_message(filters.command("fbanlist"))
async def fed_ban_list(client: Client, message: Message):
    fed_id = sql.get_fed_id(message.chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
    
    bans = sql.get_all_fban_users(fed_id)
    if not bans:
        await message.reply_text("No users are federation-banned.")
        return
    
    text = "**Banned users in this federation:**\n"
    for ban in bans:
        text += f"- `{ban['user_id']}`: {ban['reason']}\n"
    
    # In a real bot, you'd want to handle long list splitting here.
    await message.reply_text(text[:4000])

@pbot.on_message(filters.command("fednotif"))
async def fed_notif(client: Client, message: Message):
    user = message.from_user
    fed_id = sql.get_fed_id(message.chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
    
    info = sql.get_fed_info(fed_id)
    if str(info["owner"]) != str(user.id):
        await message.reply_text("Only the federation owner can toggle notifications!")
        return
    
    args = message.command[1:]
    if not args:
        await message.reply_text("Use `on` or `off`.")
        return
        
    if args[0].lower() in ("on", "yes", "true"):
        sql.set_user_feds_report(user.id, True)
        await message.reply_text("Notifications turned on!")
    elif args[0].lower() in ("off", "no", "false"):
        sql.set_user_feds_report(user.id, False)
        await message.reply_text("Notifications turned off!")
    else:
        await message.reply_text("Invalid option!")

@pbot.on_message(filters.command("fedchats"))
async def fed_chats(client: Client, message: Message):
    fed_id = sql.get_fed_id(message.chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
    
    chats = sql.all_fed_chats(fed_id)
    text = f"**Chats in this federation:**\n"
    for chat_id in chats:
        try:
            c = await client.get_chat(chat_id)
            text += f"- {c.title} (`{chat_id}`)\n"
        except:
            text += f"- `{chat_id}`\n"
            
    await message.reply_text(text[:4000])

@pbot.on_callback_query(filters.regex(r"^rm_fed_"))
async def del_fed_button(client: Client, query: CallbackQuery):
    fed_id = query.data.split("_")[-1]
    user = query.from_user
    info = sql.get_fed_info(fed_id)
    
    if str(info["owner"]) != str(user.id):
        await query.answer("You are not the owner of this federation!", show_alert=True)
        return
        
    sql.del_fed(fed_id)
    await query.message.edit_text(f"Federation {info['fname']} has been deleted.")

@pbot.on_message(filters.command("fstat"))
async def fed_stat_user(client: Client, message: Message):
    user_id = await extract_user(message, message.command[1:])
    if not user_id:
        user_id = message.from_user.id
        
    feds = sql.get_user_fban_list(user_id)
    if not feds:
        await message.reply_text("This user has no federation bans.")
        return
    
    text = f"**Federation bans for this user:**\n"
    for fed in feds:
        info = sql.get_fed_info(fed['fed_id'])
        text += f"- {info['fname']}: {fed['reason']}\n"
    await message.reply_text(text)

@pbot.on_message(filters.command("setfedlog"))
async def set_fed_log(client: Client, message: Message):
    user = message.from_user
    fed_id = sql.get_fed_id(message.chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
        
    info = sql.get_fed_info(fed_id)
    if str(info["owner"]) != str(user.id):
        await message.reply_text("Only the federation owner can set log channel!")
        return
        
    sql.set_fed_log(fed_id, message.chat.id)
    await message.reply_text("Successfully set this chat as federation log channel!")

@pbot.on_message(filters.command("unsetfedlog"))
async def unset_fed_log(client: Client, message: Message):
    user = message.from_user
    fed_id = sql.get_fed_id(message.chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
        
    info = sql.get_fed_info(fed_id)
    if str(info["owner"]) != str(user.id):
        await message.reply_text("Only the federation owner can unset log channel!")
        return
        
    sql.unset_fed_log(fed_id)
    await message.reply_text("Successfully unset federation log channel!")

@pbot.on_message(filters.command("subfed"))
async def subs_feds(client: Client, message: Message):
    user = message.from_user
    fed_id = sql.get_fed_id(message.chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
        
    info = sql.get_fed_info(fed_id)
    if str(info["owner"]) != str(user.id):
        await message.reply_text("Only the federation owner can subscribe!")
        return
        
    args = message.command[1:]
    if not args:
        await message.reply_text("Please provide a federation ID to subscribe to.")
        return
        
    target_fed_id = args[0]
    if target_fed_id == fed_id:
        await message.reply_text("You cannot subscribe to your own federation!")
        return
        
    res = sql.subs_fed(fed_id, target_fed_id)
    if res:
        await message.reply_text("Successfully subscribed to federation!")
    else:
        await message.reply_text("Already subscribed or invalid ID.")

@pbot.on_message(filters.command("unsubfed"))
async def unsubs_feds(client: Client, message: Message):
    user = message.from_user
    fed_id = sql.get_fed_id(message.chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
        
    info = sql.get_fed_info(fed_id)
    if str(info["owner"]) != str(user.id):
        await message.reply_text("Only the federation owner can unsubscribe!")
        return
        
    args = message.command[1:]
    if not args:
        await message.reply_text("Please provide a federation ID to unsubscribe from.")
        return
        
    target_fed_id = args[0]
    res = sql.unsubs_fed(fed_id, target_fed_id)
    if res:
        await message.reply_text("Successfully unsubscribed from federation!")
    else:
        await message.reply_text("Not subscribed to this federation.")

@pbot.on_message(filters.command("fedsubs"))
async def get_myfedsubs(client: Client, message: Message):
    fed_id = sql.get_fed_id(message.chat.id)
    if not fed_id:
        await message.reply_text("This group is not part of any federation!")
        return
    
    subs = sql.get_subscriber(fed_id)
    if not subs:
        await message.reply_text("You have no subscribed federations.")
        return
        
    text = "**Subscribed federations:**\n"
    for sub in subs:
        text += f"- `{sub}`\n"
    await message.reply_text(text)

@pbot.on_message(filters.command("myfeds"))
async def get_myfeds_list(client: Client, message: Message):
    user = message.from_user
    feds = sql.get_user_owner_fed_full(user.id)
    if not feds:
        await message.reply_text("You do not own any federations.")
        return
        
    text = "**Your federations:**\n"
    for fed in feds:
        text += f"- {fed['fname']} (`{fed['fed_id']}`)\n"
    await message.reply_text(text)

@pbot.on_message(filters.command("fedownerhelp"))
async def fed_owner_help(client: Client, message: Message):
    await message.reply_text(
        "**Federation Owner Help:**\n"
        "• `/newfed <name>`: Create a new federation\n"
        "• `/delfed <id>`: Delete a federation\n"
        "• `/fedname <new name>`: Rename a federation\n"
        "• `/fprom <user>`: Promote a user to fed admin\n"
        "• `/fdem <user>`: Demote a user from fed admin\n"
        "• `/setfrules <rules>`: Set federation rules\n"
        "• `/fbroadcast <message>`: Broadcast a message to all fed chats\n"
        "• `/setfedlog`: Set current chat as fed log\n"
        "• `/unsetfedlog`: Unset fed log\n"
        "• `/subfed <id>`: Subscribe to another federation\n"
        "• `/unsubfed <id>`: Unsubscribe from another federation\n"
        "• `/fednotif <on/off>`: Toggle fed notifications"
    )

@pbot.on_message(filters.command("fedadminhelp"))
async def fed_admin_help(client: Client, message: Message):
    await message.reply_text(
        "**Federation Admin Help:**\n"
        "• `/fban <user> [reason]`: Ban a user from the federation\n"
        "• `/unfban <user>`: Unban a user from the federation\n"
        "• `/fstat <user>`: Check a user's fed ban status\n"
        "• `/fedinfo <id>`: Get info about a federation\n"
        "• `/fedadmins`: List all fed admins\n"
        "• `/fedchats`: List all chats in the federation\n"
        "• `/fbanlist`: List all banned users"
    )

@pbot.on_message(filters.command("feduserhelp"))
async def fed_user_help(client: Client, message: Message):
    await message.reply_text(
        "**Federation User Help:**\n"
        "• `/fstat`: Check your own fed ban status\n"
        "• `/frules`: View the rules of the current federation"
    )

__mod_name__ = "Fed"
__help__ = """
Federations allow you to sync bans across multiple groups.
One ban in the federation affects all chats connected to it.

**Commands:**
• `/fedownerhelp`: Help for Fed owners
• `/fedadminhelp`: Help for Fed admins
• `/feduserhelp`: Help for all users
"""
