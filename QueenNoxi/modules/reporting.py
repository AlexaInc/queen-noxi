import html
from pyrogram import filters, Client, enums
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from pyrogram.errors import BadRequest, UserNotParticipant

from QueenNoxi import DRAGONS, LOGGER, TIGERS, WOLVES, pbot
from QueenNoxi.modules.helper_funcs.chat_status import user_admin, user_not_admin
from QueenNoxi.modules.log_channel import loggable
from QueenNoxi.modules.sql import reporting_sql as sql

REPORT_GROUP = 12
REPORT_IMMUNE_USERS = DRAGONS + TIGERS + WOLVES

@user_admin
async def report_setting(client: Client, message: Message):
    args = message.command
    chat = message.chat

    if chat.type == enums.ChatType.PRIVATE:
        if len(args) >= 2:
            if args[1] in ("yes", "on"):
                sql.set_user_setting(chat.id, True)
                await message.reply_text(
                    "Turned on reporting! You'll be notified whenever anyone reports something."
                )
            elif args[1] in ("no", "off"):
                sql.set_user_setting(chat.id, False)
                await message.reply_text("Turned off reporting! You wont get any reports.")
        else:
            await message.reply_text(
                f"Your current report preference is: `{sql.user_should_report(chat.id)}`"
            )
    else:
        if len(args) >= 2:
            if args[1] in ("yes", "on"):
                sql.set_chat_setting(chat.id, True)
                await message.reply_text(
                    "Turned on reporting! Admins who have turned on reports will be notified when /report or @admin is called."
                )
            elif args[1] in ("no", "off"):
                sql.set_chat_setting(chat.id, False)
                await message.reply_text(
                    "Turned off reporting! No admins will be notified on /report or @admin."
                )
        else:
            await message.reply_text(
                f"This group's current setting is: `{sql.chat_should_report(chat.id)}`"
            )

@user_not_admin
@loggable
async def report(client: Client, message: Message):
    chat = message.chat
    user = message.from_user

    if chat and message.reply_to_message and sql.chat_should_report(chat.id):
        reported_user = message.reply_to_message.from_user
        if not reported_user:
            return ""
            
        chat_name = chat.title or chat.first_name
        
        # In Pyrogram we need to get admins one by one or via get_chat_members(filter=enums.ChatMembersFilter.ADMINISTRATORS)
        admin_list = []
        async for m in client.get_chat_members(chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admin_list.append(m)

        if len(message.command) <= 0 and not message.text.startswith("@admin"):
             # This happens if it was triggered by regex @admin but no reason was given as a message? 
             # Actually @admin trigger often has no reason in command[1:]
             pass

        if user.id == reported_user.id:
            await message.reply_text("Uh yeah, Sure sure...maso much?")
            return ""

        if reported_user.id == client.me.id:
            await message.reply_text("Nice try.")
            return ""

        if reported_user.id in REPORT_IMMUNE_USERS:
            await message.reply_text("Uh? You reporting a disaster?")
            return ""

        reported_mention = f"[{user.first_name}](tg://user?id={user.id})"
        reported_user_mention = f"[{reported_user.first_name}](tg://user?id={reported_user.id})"

        msg = (
            f"<b>⚠️ Report: </b>{html.escape(chat_name)}\n"
            f"<b> • Report by:</b> {user.mention} (<code>{user.id}</code>)\n"
            f"<b> • Reported user:</b> {reported_user.mention} (<code>{reported_user.id}</code>)\n"
        )
        
        reply_markup = None
        if chat.username:
            link = f'<b> • Reported message:</b> <a href="https://t.me/{chat.username}/{message.reply_to_message.id}">click here</a>'
            keyboard = [
                [
                    InlineKeyboardButton(
                        "➡ Message",
                        url=f"https://t.me/{chat.username}/{message.reply_to_message.id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⚠ Kick",
                        callback_data=f"report_{chat.id}=kick={reported_user.id}",
                    ),
                    InlineKeyboardButton(
                        "⛔️ Ban",
                        callback_data=f"report_{chat.id}=banned={reported_user.id}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "❎ Delete Message",
                        callback_data=f"report_{chat.id}=delete={reported_user.id}={message.reply_to_message.id}",
                    )
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            link = ""

        count = 0
        for admin in admin_list:
            if admin.user.is_bot:
                continue

            if sql.user_should_report(admin.user.id):
                try:
                    await client.send_message(
                        admin.user.id,
                        msg + link,
                        reply_markup=reply_markup,
                    )
                    count += 1
                except Exception:
                    pass

        if count > 0:
            await message.reply_to_message.reply_text(
                f"{user.mention} reported the message to the admins."
            )
            return msg
    return ""

async def buttons(client: Client, query: CallbackQuery):
    splitter = query.data.replace("report_", "").split("=")
    chat_id = int(splitter[0])
    action = splitter[1]
    user_id = int(splitter[2])

    # Check if the person clicking the button is an admin in that chat
    try:
        member = await client.get_chat_member(chat_id, query.from_user.id)
        if member.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
            await query.answer("You must be an admin to do this!", show_alert=True)
            return
    except Exception:
        await query.answer("Error checking your permissions", show_alert=True)
        return

    if action == "kick":
        try:
            await client.ban_chat_member(chat_id, user_id)
            await client.unban_chat_member(chat_id, user_id)
            await query.answer("✅ Successfully kicked")
        except Exception as err:
            await query.answer(f"🛑 Failed to kick: {err}", show_alert=True)

    elif action == "banned":
        try:
            await client.ban_chat_member(chat_id, user_id)
            await query.answer("✅ Successfully Banned")
        except Exception as err:
            await query.answer(f"🛑 Failed to Ban: {err}", show_alert=True)

    elif action == "delete":
        try:
            msg_id = int(splitter[3])
            await client.delete_messages(chat_id, msg_id)
            await query.answer("✅ Message Deleted")
        except Exception as err:
            await query.answer(f"🛑 Failed to delete message: {err}", show_alert=True)

@pbot.on_message(filters.command("reports") & (filters.group | filters.private))
async def reports_handler(client, message):
    await report_setting(client, message)

@pbot.on_message(filters.command("report") & filters.group)
async def report_cmd_handler(client, message):
    await report(client, message)

@pbot.on_message(filters.regex(r"(?i)@admin(s)?") & filters.group)
async def admin_report_handler(client, message):
    await report(client, message)

@pbot.on_callback_query(filters.regex(r"report_"))
async def report_button_handler(client, query):
    await buttons(client, query)

__mod_name__ = "Rᴇᴘᴏʀᴛ s​"
__help__ = """
 ❍ /ʀᴇᴘᴏʀᴛ <ʀᴇᴀsᴏɴ>*:* ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴛᴏ ᴀᴅᴍɪɴs.
 ❍ @ᴀᴅᴍɪɴ*:* ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴛᴏ ᴀᴅᴍɪɴs.
  
*ɴᴏᴛᴇ :* ɴᴇɪᴛʜᴇʀ ᴏғ ᴛʜᴇsᴇ ᴡɪʟʟ ɢᴇᴛ ᴛʀɪɢɢᴇʀᴇᴅ ɪғ ᴜsᴇᴅ ʙʏ ᴀᴅᴍɪɴs.

*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
 ❍ /ʀᴇᴘᴏʀᴛs <ᴏɴ/ᴏғғ>*:* ᴄʜᴀɴɢᴇ ʀᴇᴘᴏʀᴛ sᴇᴛᴛɪɴɢ, ᴏʀ ᴠɪᴇᴡ ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs.
   • ɪғ ᴅᴏɴᴇ ɪɴ ᴘᴍ, ᴛᴏɢɢʟᴇs ʏᴏᴜʀ sᴛᴀᴛᴜs.
   • ɪғ ɪɴ ɢʀᴏᴜᴘ, ᴛᴏɢɢʟᴇs ᴛʜᴀᴛ ɢʀᴏᴜᴘs's sᴛᴀᴛᴜs.
"""
