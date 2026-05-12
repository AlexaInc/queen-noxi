import html
from pyrogram import filters, Client, enums
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from pyrogram.errors import RPCError

import QueenNoxi.modules.sql.approve_sql as sql
from QueenNoxi import DRAGONS, pbot
from QueenNoxi.modules.disable import DisableAbleCommandHandler
from QueenNoxi.modules.helper_funcs.chat_status import user_admin, is_user_admin
from QueenNoxi.modules.helper_funcs.extraction import extract_user
from QueenNoxi.modules.log_channel import loggable

@pbot.on_message(filters.command("approve") & filters.group)
@DisableAbleCommandHandler("approve")
@user_admin
@loggable
async def approve(client: Client, message: Message) -> str:
    chat = message.chat
    user = message.from_user
    user_id = await extract_user(message, message.command[1:])
    if not user_id:
        await message.reply_text("I don't know who you're talking about, you're going to need to specify a user!")
        return ""
    
    try:
        member = await chat.get_member(user_id)
    except RPCError:
        return ""
        
    if member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        await message.reply_text("User is already admin - locks, blocklists, and antiflood already don't apply to them.")
        return ""
        
    if sql.is_approved(chat.id, user_id):
        await message.reply_text(f"{member.user.mention} is already approved in {chat.title}")
        return ""
        
    sql.approve(chat.id, user_id)
    await message.reply_text(f"{member.user.mention} has been approved in {chat.title}! They will now be ignored by automated admin actions like locks, blocklists, and antiflood.")
    
    return f"<b>{html.escape(chat.title)}:</b>\n#APPROVED\n<b>Admin:</b> {user.mention}\n<b>User:</b> {member.user.mention}"

@pbot.on_message(filters.command("unapprove") & filters.group)
@DisableAbleCommandHandler("unapprove")
@user_admin
@loggable
async def disapprove(client: Client, message: Message) -> str:
    chat = message.chat
    user = message.from_user
    user_id = await extract_user(message, message.command[1:])
    if not user_id:
        await message.reply_text("I don't know who you're talking about, you're going to need to specify a user!")
        return ""
        
    try:
        member = await chat.get_member(user_id)
    except RPCError:
        return ""
        
    if member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        await message.reply_text("This user is an admin, they can't be unapproved.")
        return ""
        
    if not sql.is_approved(chat.id, user_id):
        await message.reply_text(f"{member.user.first_name} isn't approved yet!")
        return ""
        
    sql.disapprove(chat.id, user_id)
    await message.reply_text(f"{member.user.first_name} is no longer approved in {chat.title}.")
    
    return f"<b>{html.escape(chat.title)}:</b>\n#UNAPPROVED\n<b>Admin:</b> {user.mention}\n<b>User:</b> {member.user.mention}"

@pbot.on_message(filters.command("approved") & filters.group)
@DisableAbleCommandHandler("approved")
@user_admin
async def approved(client: Client, message: Message):
    chat = message.chat
    msg = "The following users are approved.\n"
    approved_users = sql.list_approved(chat.id)
    for i in approved_users:
        try:
            member = await chat.get_member(int(i.user_id))
            msg += f"- `{i.user_id}`: {member.user.first_name}\n"
        except:
            msg += f"- `{i.user_id}`\n"
            
    if msg.endswith("approved.\n"):
        await message.reply_text(f"No users are approved in {chat.title}.")
    else:
        await message.reply_text(msg)

@pbot.on_message(filters.command("approval") & filters.group)
@DisableAbleCommandHandler("approval")
@user_admin
async def approval(client: Client, message: Message):
    chat = message.chat
    user_id = await extract_user(message, message.command[1:])
    if not user_id:
        await message.reply_text("I don't know who you're talking about, you're going to need to specify a user!")
        return ""
        
    member = await chat.get_member(int(user_id))
    if sql.is_approved(chat.id, user_id):
        await message.reply_text(f"{member.user.first_name} is an approved user. Locks, antiflood, and blocklists won't apply to them.")
    else:
        await message.reply_text(f"{member.user.first_name} is not an approved user. They are affected by normal commands.")

@pbot.on_message(filters.command("unapproveall") & filters.group)
@DisableAbleCommandHandler("unapproveall")
async def unapproveall(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    member = await chat.get_member(user.id)
    if member.status != enums.ChatMemberStatus.OWNER and user.id not in DRAGONS:
        await message.reply_text("Only the chat owner can unapprove all users at once.")
        return

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="Unapprove all users", callback_data="unapproveall_user")],
            [InlineKeyboardButton(text="Cancel", callback_data="unapproveall_cancel")],
        ]
    )
    await message.reply_text(
        f"Are you sure you would like to unapprove ALL users in {chat.title}? This action cannot be undone.",
        reply_markup=buttons,
    )

@pbot.on_callback_query(filters.regex(r"unapproveall_.*"))
async def unapproveall_btn(client: Client, query: CallbackQuery):
    chat = query.message.chat
    user_id = query.from_user.id
    member = await chat.get_member(user_id)
    
    if query.data == "unapproveall_user":
        if member.status == enums.ChatMemberStatus.OWNER or user_id in DRAGONS:
            approved_users = sql.list_approved(chat.id)
            for i in approved_users:
                sql.disapprove(chat.id, int(i.user_id))
            await query.message.edit_text("Successfully unapproved all users.")
        else:
            await query.answer("Only the owner of the chat can do this.", show_alert=True)
            
    elif query.data == "unapproveall_cancel":
        if member.status == enums.ChatMemberStatus.OWNER or user_id in DRAGONS:
            await query.message.edit_text("Removing of all approved users has been cancelled.")
        else:
            await query.answer("Only the owner of the chat can do this.", show_alert=True)

__mod_name__ = "Approve"
__help__ = """
Some users might be trustworthy enough to be ignored by automated admin actions.
Approval allows them to be bypassed by locks, blocklists, and antiflood.

**Admin Commands:**
• `/approval`: Check a user's approval status
• `/approve`: Approve a user
• `/unapprove`: Unapprove a user
• `/approved`: List all approved users
• `/unapproveall`: Unapprove ALL users (Owner only)
"""
