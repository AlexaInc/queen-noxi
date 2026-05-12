from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from QueenNoxi import pbot as app, BOT_ID, DRAGONS as DEVS, OWNER_ID
from QueenNoxi.modules.no_sql import fsub_db as db

async def check_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member.privileges:
            return True
    except Exception:
        pass
    return False

@app.on_message(filters.command(["fsub", "forcesubscribe", "Forcesubscribe", "Forcesub"]))
async def fsub_cmd(_, message):
    if message.chat.type.name == "PRIVATE":
        return
    try:
        member = await app.get_chat_member(message.chat.id, message.from_user.id)
    except Exception:
        return
        
    if not member.privileges:
        return await message.reply("ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ᴛʜɪs.")
    if member.status.name != "OWNER":
        return await message.reply("❗ <b>ɢʀᴏᴜᴘ ᴄʀᴇᴀᴛᴏʀ ʀᴇǫᴜɪʀᴇᴅ</b> \n<i>ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ʙᴇ ᴛʜᴇ ɢʀᴏᴜᴘ ᴄʀᴇᴀᴛᴏʀ ᴛᴏ ᴅᴏ ᴛʜᴀᴛ.</i>", parse_mode="html")
        
    channel = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not channel:
        chat_db = db.fs_settings(message.chat.id)
        if not chat_db:
            await message.reply("<b>❌ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ɪs ᴅɪsᴀʙʟᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.</b>")
        else:
            await message.reply(f"ғᴏʀᴄᴇsᴜʙsᴄʀɪʙᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ <b>ᴇɴᴀʙʟᴇᴅ</b>. ᴜsᴇʀs ᴀʀᴇ ғᴏʀᴄᴇᴅ ᴛᴏ ᴊᴏɪɴ <b>@{chat_db.channel}</b> ᴛᴏ sᴘᴇᴀᴋ ʜᴇʀᴇ.")
    elif channel in ["on", "yes", "y"]:
        await message.reply("❗ᴘʟᴇᴀsᴇ sᴘᴇᴄɪғʏ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ.")
    elif channel in ["off", "no", "n"]:
        await message.reply("**❌ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ɪs ᴅɪsᴀʙʟᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.**")
        db.disapprove(message.chat.id)
    else:
        try:
            channel_entity = await app.get_chat(channel)
            if channel_entity.type.name != "CHANNEL":
                return await message.reply("ᴛʜᴀᴛ's ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ.")
        except Exception:
            return await message.reply("❗<b>ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ ᴘʀᴏᴠɪᴅᴇᴅ.</b>")
            
        channel_username = channel_entity.username
        try:
            member = await app.get_chat_member(channel_entity.id, app.me.id)
            if not member.privileges:
                return await message.reply(f"❗**ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ**\nI ᴀᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ. ᴀᴅᴅ ᴍᴇ ᴀs ᴀ ᴀᴅᴍɪɴ ɪɴ ᴏʀᴅᴇʀ ᴛᴏ ᴇɴᴀʙʟᴇ ғᴏʀᴄᴇsᴜʙsᴄʀɪʙᴇ.")
        except Exception:
            return await message.reply("I am not in that channel.")
            
        db.add_channel(message.chat.id, str(channel_username))
        await message.reply(f"✅ **ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ɪs ᴇɴᴀʙʟᴇᴅ** to @{channel_username}.")

@app.on_message(~filters.private, group=10)
async def fsub_n(_, message):
    if not db.fs_settings(message.chat.id):
        return
    if getattr(message, "forward_from", None) or getattr(message, "sender_chat", None):
        return
    if not message.from_user:
        return
        
    try:
        bot_member = await app.get_chat_member(message.chat.id, app.me.id)
        if not bot_member.privileges or not bot_member.privileges.can_restrict_members:
            return
    except Exception:
        return
        
    if await check_admin(message.chat.id, message.from_user.id) or message.from_user.id in DEVS or message.from_user.id == OWNER_ID:
        return
        
    channel = (db.fs_settings(message.chat.id)).get("channel")
    try:
        await app.get_chat_member(channel, message.from_user.id)
        check = True
    except UserNotParticipant:
        check = False
    except Exception:
        check = True
        
    if not check:
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{channel}")],
            [InlineKeyboardButton("ᴜɴᴍᴜᴛᴇ ᴍᴇ", callback_data=f"fs_{message.from_user.id}")]
        ])
        txt = f'<b><a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a></b>, ʏᴏᴜ ʜᴀᴠᴇ <b>ɴᴏᴛ sᴜʙsᴄʀɪʙᴇᴅ</b> ᴛᴏ ᴏᴜʀ <b><a href="t.me/{channel}">ᴄʜᴀɴɴᴇʟ</a></b> ʏᴇᴛ❗.ᴘʟᴇᴀsᴇ <b><a href="t.me/{channel}">ᴊᴏɪɴ</a></b> ᴀɴᴅ <b>ᴘʀᴇss ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ</b> ᴛᴏ ᴜɴᴍᴜᴛᴇ ʏᴏᴜʀsᴇʟғ.'
        await message.reply(txt, reply_markup=buttons, disable_web_page_preview=True)
        try:
            await app.restrict_chat_member(message.chat.id, message.from_user.id, ChatPermissions(can_send_messages=False))
        except Exception:
            pass

@app.on_callback_query(filters.regex(r"^fs\_(\d+)"))
async def unmute_fsub(_, query):
    user_id = int(query.matches[0].group(1))
    if query.from_user.id != user_id:
        return await query.answer("ᴛʜɪs ɪs ɴᴏᴛ ᴍᴇᴀɴᴛ ғᴏʀ ʏᴏᴜ.", show_alert=True)
        
    channel = (db.fs_settings(query.message.chat.id)).get("channel")
    try:
        await app.get_chat_member(channel, user_id)
        check = True
    except UserNotParticipant:
        check = False
    except Exception:
        check = True
        
    if not check:
        return await query.answer("ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ғɪʀsᴛ, ᴛᴏ ɢᴇᴛ ᴜɴᴍᴜᴛᴇᴅ!", show_alert=True)
        
    try:
        await app.restrict_chat_member(query.message.chat.id, user_id, ChatPermissions(
            can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True
        ))
    except Exception:
        pass
    await query.message.delete()

__mod_name__ = "F-sᴜʙ"

__help__="""
*ғᴏʀᴄᴇ ꜱᴜʙꜱᴄʀɪʙᴇ:*

   •➥ *ᴍᴜᴋᴇsʜʀᴏʙᴏᴛ ᴄᴀɴ ᴍᴜᴛᴇ ᴍᴇᴍʙᴇʀꜱ ᴡʜᴏ ᴀʀᴇ ɴᴏᴛ ꜱᴜʙꜱᴄʀɪʙᴇᴅ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴜɴᴛɪʟ ᴛʜᴇʏ ꜱᴜʙꜱᴄʀɪʙᴇ*
   •➥ ᴡʜᴇɴ ᴇɴᴀʙʟᴇᴅ ɪ ᴡɪʟʟ ᴍᴜᴛᴇ ᴜɴꜱᴜʙꜱᴄʀɪʙᴇᴅ ᴍᴇᴍʙᴇʀꜱ ᴀɴᴅ ꜱʜᴏᴡ ᴛʜᴇᴍ ᴀ ᴜɴᴍᴜᴛᴇ ʙᴜᴛᴛᴏɴ. ᴡʜᴇɴ ᴛʜᴇʏ ᴘʀᴇꜱꜱᴇᴅ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ɪ ᴡɪʟʟ ᴜɴᴍᴜᴛᴇ ᴛʜᴇᴍ

   •➥ *ꜱᴇᴛᴜᴘ*
   •➥ [ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀꜱ ᴀᴅᴍɪɴ](https://t.me/groupcontrollertgbot?startgroup=new)
   •➥ [ᴀᴅᴅ ᴍᴇ ɪɴ your ᴄʜᴀɴɴᴇʟ ᴀꜱ ᴀᴅᴍɪɴ](https://t.me/groupcontrollertgbot?startgroup=new)
 
    *ᴄᴏᴍᴍᴍᴀɴᴅꜱ*
   •➥ /fsub channel username - ᴛᴏ ᴛᴜʀɴ ᴏɴ ᴀɴᴅ sᴇᴛᴜᴘ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ.
   •➥ /fsub off - ᴛᴏ ᴛᴜʀɴ ᴏғ ғᴏʀᴄᴇꜱᴜʙꜱᴄʀɪʙᴇ..
   💡 ɪғ ʏᴏᴜ ᴅɪꜱᴀʙʟᴇ ғꜱᴜʙ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ꜱᴇᴛ ᴀɢᴀɪɴ ғᴏʀ ᴡᴏʀᴋɪɴɢ /fsub channel username
 
"""
