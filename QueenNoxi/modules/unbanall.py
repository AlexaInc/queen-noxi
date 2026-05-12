from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import ChatPermissions
from QueenNoxi import pbot as app, LOGGER
import asyncio

async def check_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.privileges is not None
    except Exception:
        return False

@app.on_message(filters.command("unbanall"))
async def unbanall_cmd(_, message):
    if message.chat.type.name == "PRIVATE":
        return await message.reply("__ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴜsᴇ ɪɴ ɢʀᴏᴜᴘs ᴀɴᴅ ᴄʜᴀɴɴᴇʟs!__")
    if not await check_admin(message.chat.id, message.from_user.id):
        return await message.reply("__ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴍᴜᴛᴇᴀʟʟ!__")
    
    bot_member = await app.get_chat_member(message.chat.id, app.me.id)
    if not bot_member.privileges or not bot_member.privileges.can_restrict_members:
        return await message.reply("`I don't have enough permissions!`")
        
    done = await message.reply("sᴇᴀʀᴄʜɪɴɢ ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ ʟɪsᴛs")
    p = 0
    try:
        async for member in app.get_chat_members(message.chat.id, filter=ChatMembersFilter.BANNED):
            try:
                await app.unban_chat_member(message.chat.id, member.user.id)
                p += 1
            except Exception:
                pass
    except Exception as e:
        LOGGER.error(f"Unbanall error: {e}")
            
    if p == 0:
        await done.edit("ɴᴏ ᴏɴᴇ ɪs ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ")
    else:
        await done.edit(f"sᴜᴄᴇssғᴜʟʟʏ ᴜɴʙᴀɴɴᴇᴅ **{p}** ᴜsᴇʀs")

@app.on_message(filters.command("unmuteall"))
async def unmuteall_cmd(_, message):
    if message.chat.type.name == "PRIVATE":
        return await message.reply("__This command can be use in groups and channels!__")
    if not await check_admin(message.chat.id, message.from_user.id):
        return await message.reply("__ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴍᴜᴛᴇᴀʟʟ!__")
    
    bot_member = await app.get_chat_member(message.chat.id, app.me.id)
    if not bot_member.privileges or not bot_member.privileges.can_restrict_members:
        return await message.reply("`I don't have enough permissions!`")
        
    done = await message.reply("Working ...")
    p = 0
    try:
        async for member in app.get_chat_members(message.chat.id, filter=ChatMembersFilter.RESTRICTED):
            try:
                await app.restrict_chat_member(message.chat.id, member.user.id, ChatPermissions(
                    can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True
                ))
                p += 1
            except Exception:
                pass
    except Exception as e:
         LOGGER.error(f"unmuteall error: {e}")
            
    if p == 0:
        await done.edit("ɴᴏ ᴏɴᴇ ɪs ᴍᴜᴛᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ")
    else:
        await done.edit(f"sᴜᴄᴇssғᴜʟʟʏ ᴜɴᴍᴜᴛᴇᴅ **{p}** ᴜsᴇʀs")

@app.on_message(filters.command("users"))
async def users_cmd(_, message):
    if message.chat.type.name == "PRIVATE":
        return
    if not await check_admin(message.chat.id, message.from_user.id):
        return
    title = message.chat.title or "this chat"
    mentions = f"ᴜsᴇʀs ɪɴ {title}: \n"
    async for member in app.get_chat_members(message.chat.id):
        if member.user.is_deleted:
            mentions += f"\nᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs  {member.user.id}"
        else:
            mentions += f"\n[{member.user.first_name}](tg://user?id={member.user.id}) ❣ {member.user.id}"
            
    with open("userslist.txt", "w+", encoding="utf-8") as file:
        file.write(mentions)
    await message.reply_document("userslist.txt", caption=f"ᴜsᴇʀs ɪɴ {title}")
    import os; os.remove("userslist.txt")

__mod_name__ = "Aᴅᴠᴀɴᴄᴇ"
__help__ = """
➥ /unbanall : ᴜɴʙᴀɴ ᴀʟʟ ᴍᴀᴍʙᴇʀ 
➥ /unmuteall : ᴜɴᴍᴜᴛᴇ ᴀʟʟ ᴍᴀᴍʙᴇʀ
➥ /users : ɢᴇᴛ ɢʀᴏᴜᴘ ᴜsᴇʀs ʟɪsᴛ
"""
