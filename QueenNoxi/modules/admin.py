import html
import os
from pyrogram import filters, Client, enums
from pyrogram.raw import functions, types as raw_types
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPrivileges
)
from pyrogram.errors import RPCError

from QueenNoxi import DRAGONS, pbot, BOT_ID
from QueenNoxi.modules.disable import DisableAbleCommandHandler
from QueenNoxi.modules.helper_funcs.admin_rights import user_can_changeinfo
from QueenNoxi.modules.helper_funcs.chat_status import (
    bot_admin,
    can_pin,
    connection_status,
    user_admin,
    can_promote,
    is_user_admin
)
from QueenNoxi.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from QueenNoxi.modules.log_channel import loggable

@pbot.on_message(filters.command("setsticker") & filters.group)
@bot_admin
@user_admin
async def set_sticker(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    if not await user_can_changeinfo(chat.id, user.id):
        return await message.reply_text("» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴩ ɪɴғᴏ ʙᴀʙʏ !")

    if message.reply_to_message and message.reply_to_message.sticker:
        stkr = message.reply_to_message.sticker.set_name
        try:
            await client.set_chat_sticker_set(chat.id, stkr)
            await message.reply_text(f"» sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ɢʀᴏᴜᴩ sᴛɪᴄᴋᴇʀs ɪɴ {chat.title}!")
        except RPCError as e:
            await message.reply_text(f"Error: {e.MESSAGE}")
    else:
        await message.reply_text("» ʀᴇᴩʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴛᴏ sᴇᴛ ɪᴛ ᴀs ɢʀᴏᴜᴩ sᴛɪᴄᴋᴇʀ ᴩᴀᴄᴋ !")

@pbot.on_message(filters.command("setgpic") & filters.group)
@bot_admin
@user_admin
async def setchatpic(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    if not await user_can_changeinfo(chat.id, user.id):
        return await message.reply_text("» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴩ ɪɴғᴏ ʙᴀʙʏ !")

    if message.reply_to_message and (message.reply_to_message.photo or message.reply_to_message.document):
        dlmsg = await message.reply_text("» ᴄʜᴀɴɢɪɴɢ ɢʀᴏᴜᴩ's ᴩʀᴏғɪʟᴇ ᴩɪᴄ...")
        img = await message.reply_to_message.download("gpic.png")
        try:
            await client.set_chat_photo(chat.id, photo=img)
            await message.reply_text("» sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ɢʀᴏᴜᴩ ᴩʀᴏғɪʟᴇ ᴩɪᴄ !")
        except RPCError as e:
            await message.reply_text(f"Error: {e.MESSAGE}")
        finally:
            await dlmsg.delete()
            if os.path.exists("gpic.png"):
                os.remove("gpic.png")
    else:
        await message.reply_text("» ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴩʜᴏᴛᴏ ᴏʀ ғɪʟᴇ ᴛᴏ sᴇᴛ ɪᴛ ᴀs ɢʀᴏᴜᴩ ᴩʀᴏғɪʟᴇ ᴩɪᴄ !")

@pbot.on_message(filters.command("delgpic") & filters.group)
@bot_admin
@user_admin
async def rmchatpic(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    if not await user_can_changeinfo(chat.id, user.id):
        return await message.reply_text("» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏUtᴩ ɪɴғᴏ ʙᴀʙʏ !")
    try:
        await client.delete_chat_photo(chat.id)
        await message.reply_text("» sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ɢʀᴏᴜᴩ's ᴅᴇғᴀᴜʟᴛ ᴩʀᴏғɪʟᴇ ᴩɪᴄ !")
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")

@pbot.on_message(filters.command("setdesc") & filters.group)
@bot_admin
@user_admin
async def set_desc(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    if not await user_can_changeinfo(chat.id, user.id):
        return await message.reply_text("» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴩ ɪɴғᴏ ʙᴀʙʏ !")

    desc = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not desc:
        return await message.reply_text("» ᴡᴛғ, ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴇᴛ ᴀɴ ᴇᴍᴩᴛʏ ᴅᴇsᴄʀɪᴩᴛɪᴏɴ !")
    try:
        await client.set_chat_description(chat.id, desc[:255])
        await message.reply_text(f"» sᴜᴄᴄᴇssғᴜʟʟʏ ᴜᴩᴅᴀᴛᴇᴅ ᴄʜᴀᴛ ᴅᴇsᴄʀɪᴩᴛɪᴏɴ ɪɴ {chat.title}!")
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")

@pbot.on_message(filters.command("setgtitle") & filters.group)
@bot_admin
@user_admin
async def setchat_title(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    if not await user_can_changeinfo(chat.id, user.id):
        return await message.reply_text("» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴩ ɪɴғᴏ ʙᴀʙʏ !")

    title = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not title:
        return await message.reply_text("» ᴇɴᴛᴇʀ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ sᴇᴛ ɪᴛ ᴀs ɴᴇᴡ ᴄʜᴀᴛ ᴛɪᴛʟᴇ !")
    try:
        await client.set_chat_title(chat.id, title)
        await message.reply_text(f"» sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ <b>{html.escape(title)}</b> ᴀs ɴᴇᴡ ᴄʜᴀᴛ ᴛɪᴛʟᴇ !")
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")

@DisableAbleCommandHandler("promote", admin_ok=True)
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
async def promote(client: Client, message: Message) -> str:
    chat = message.chat
    user = message.from_user
    user_id = await extract_user(message, message.command[1:])
    if not user_id:
        await message.reply_text("» ɪ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ᴡʜᴏ's ᴛʜᴀᴛ ᴜsᴇʀ.")
        return
    try:
        user_member = await chat.get_member(user_id)
    except:
        return
    if user_member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        await message.reply_text("» ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴍᴇ ᴛʜᴀᴛ ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ ʜᴇʀᴇ !")
        return
    if user_id == BOT_ID:
        await message.reply_text("» ɪ ᴄᴀɴ'ᴛ ᴩʀᴏᴍᴏᴛᴇ ᴍʏsᴇʟғ.")
        return

    bot_member = await chat.get_member(BOT_ID)
    try:
        await client.promote_chat_member(chat.id, user_id, privileges=bot_member.privileges)
        await message.reply_text(f"» ᴩʀᴏᴍᴏᴛɪɴɢ ᴀ ᴜsᴇʀ ɪɴ {chat.title}")
        return f"<b>{html.escape(chat.title)}:</b>\n#ᴩʀᴏᴍᴏᴛᴇᴅ\n<b>ᴩʀᴏᴍᴏᴛᴇʀ :</b> {user.mention}\n<b>ᴜsᴇʀ :</b> {user_member.user.mention}"
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")

@DisableAbleCommandHandler("demote", admin_ok=True)
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
async def demote(client: Client, message: Message) -> str:
    chat = message.chat
    user = message.from_user
    user_id = await extract_user(message, message.command[1:])
    if not user_id:
        await message.reply_text("» ɪ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ᴡʜᴏ's ᴛʜᴀᴛ ᴜsᴇʀ.")
        return
    try:
        user_member = await chat.get_member(user_id)
    except:
        return
    if user_member.status == enums.ChatMemberStatus.OWNER:
        return await message.reply_text("» ᴛʜᴀᴛ ᴜsᴇʀ ɪs ᴏᴡɴᴇʀ !")
    if user_id == BOT_ID:
        return await message.reply_text("» ɪ ᴄᴀɴ'ᴛ ᴅᴇᴍᴏᴛᴇ ᴍʏsᴇʟғ.")

    try:
        # Use raw API to fully strip admin — promote_chat_member with all False
        # keeps the admin badge in Telegram; raw EditAdmin actually removes it.
        channel = await client.resolve_peer(chat.id)
        target  = await client.resolve_peer(user_id)
        await client.invoke(
            functions.channels.EditAdmin(
                channel=channel,
                user_id=target,
                admin_rights=raw_types.ChatAdminRights(
                    change_info=False,
                    post_messages=False,
                    edit_messages=False,
                    delete_messages=False,
                    ban_users=False,
                    invite_users=False,
                    pin_messages=False,
                    add_admins=False,
                    manage_call=False,
                    anonymous=False,
                    manage_topics=False,
                    post_stories=False,
                    edit_stories=False,
                    delete_stories=False,
                ),
                rank=""
            )
        )
        await message.reply_text(f"» sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇᴍᴏᴛᴇᴅ ɪɴ {chat.title}")
        return f"<b>{html.escape(chat.title)}:</b>\n#ᴅᴇᴍᴏᴛᴇᴅ\n<b>ᴅᴇᴍᴏᴛᴇʀ :</b> {user.mention}\n<b>ᴅᴇᴍᴏᴛᴇᴅ :</b> {user_member.user.mention}"
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")




@pbot.on_message(filters.command(["admincache", "reload", "refresh"]) & filters.group)
@user_admin
async def refresh_admin(client: Client, message: Message):
    from QueenNoxi.modules.helper_funcs.chat_status import ADMIN_CACHE
    try:
        ADMIN_CACHE.pop(message.chat.id)
    except KeyError:
        pass
    await message.reply_text("» sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇғʀᴇsʜᴇᴅ ᴀᴅᴍɪɴ ᴄᴀᴄʜᴇ !")

@pbot.on_message(filters.command("pin") & filters.group)
@bot_admin
@can_pin
@user_admin
@loggable
async def pin(client: Client, message: Message) -> str:
    args = message.command[1:]
    chat = message.chat
    user = message.from_user
    if not message.reply_to_message:
        return await message.reply_text("» ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴩɪɴ ɪᴛ !")

    is_silent = True
    if len(args) >= 1:
        is_silent = args[0].lower() not in ["notify", "loud", "violent"]
    try:
        await client.pin_chat_message(chat.id, message.reply_to_message.id, disable_notification=is_silent)
        await message.reply_text("» sᴜᴄᴄᴇssғᴜʟʟʏ ᴩɪɴɴᴇᴅ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ.")
        return f"<b>{html.escape(chat.title)}:</b>\nᴩɪɴɴᴇᴅ-ᴀ-ᴍᴇssᴀɢᴇ\n<b>ᴩɪɴɴᴇᴅ ʙʏ :</b> {user.mention}"
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")

@pbot.on_message(filters.command("unpin") & filters.group)
@bot_admin
@can_pin
@user_admin
@loggable
async def unpin(client: Client, message: Message) -> str:
    chat = message.chat
    user = message.from_user
    try:
        if message.reply_to_message:
            await client.unpin_chat_message(chat.id, message.reply_to_message.id)
        else:
            await client.unpin_chat_message(chat.id)
        await message.reply_text("» sᴜᴄᴄᴇssғᴜʟʟʏ ᴜɴᴩɪɴɴᴇᴅ.")
        return f"<b>{html.escape(chat.title)}:</b>\nᴜɴᴩɪɴɴᴇᴅ-ᴀ-ᴍᴇssᴀɢᴇ\n<b>ᴜɴᴩɪɴɴᴇᴅ ʙʏ :</b> {user.mention}"
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")

@DisableAbleCommandHandler("invitelink", admin_ok=True)
@connection_status
@bot_admin
async def invite(client: Client, message: Message):
    chat = message.chat
    if chat.username:
        return await message.reply_text(f"https://t.me/{chat.username}")
    try:
        invitelink = await client.export_chat_invite_link(chat.id)
        await message.reply_text(invitelink)
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")

@DisableAbleCommandHandler("title", admin_ok=True)
@connection_status
@bot_admin
@user_admin
async def set_admin_title(client: Client, message: Message):
    chat = message.chat
    user_id, title = await extract_user_and_text(message, message.command[1:])
    if not user_id:
        return await message.reply_text("» ɪ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ᴡʜᴏ's ᴛʜᴀᴛ ᴜsᴇʀ.")
    try:
        user_member = await chat.get_member(user_id)
    except:
        return
    if user_member.status == enums.ChatMemberStatus.OWNER:
        return await message.reply_text("» ᴛʜᴀᴛ ᴜsᴇʀ ɪs ᴏᴡɴᴇʀ !")
    if user_member.status != enums.ChatMemberStatus.ADMINISTRATOR:
        return await message.reply_text("» ɪ ᴄᴀɴ ᴏɴʟʏ sᴇᴛ ᴛɪᴛʟᴇ ғᴏʀ ᴀᴅᴍɪɴs !")
    if not title:
        return await message.reply_text("» sᴇᴛ ᴀ ᴛɪᴛʟᴇ ʙᴀʙʏ !")

    try:
        await client.set_administrator_custom_title(chat.id, user_id, title[:16])
        await message.reply_text(f"» sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ᴛɪᴛʟᴇ ғᴏʀ <code>{user_member.user.first_name}</code>")
    except RPCError as e:
        await message.reply_text(f"Error: {e.MESSAGE}")

@pbot.on_message(filters.command("pinned") & filters.group)
@bot_admin
async def pinned_msg(client: Client, message: Message):
    chat = await client.get_chat(message.chat.id)
    if chat.pinned_message:
        pinned_id = chat.pinned_message.id
        link = f"https://t.me/{chat.username}/{pinned_id}" if chat.username else f"https://t.me/c/{str(chat.id).replace('-100', '')}/{pinned_id}"
        await message.reply_text(f"ᴩɪɴɴᴇᴅ ᴏɴ {html.escape(chat.title)}.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴍᴇssᴀɢᴇ", url=link)]]), disable_web_page_preview=True)
    else:
        await message.reply_text(f"» ᴛʜᴇʀᴇ's ɴᴏ ᴩɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ ɪɴ <b>{html.escape(chat.title)}!</b>")

@DisableAbleCommandHandler(["admins", "staff"])
@connection_status
async def adminlist(client: Client, message: Message):
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text("» ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜsᴇᴅ ɪɴ ɢʀᴏᴜᴩ's.")
    msg = await message.reply_text("» ғᴇᴛᴄʜɪɴɢ ᴀᴅᴍɪɴs ʟɪsᴛ...")
    try:
        administrators = []
        async for m in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            administrators.append(m)
        text = "ᴀᴅᴍɪɴs ɪɴ <b>{}</b>:".format(html.escape(message.chat.title))
        creator = None; admins = []; bots = []
        for admin in administrators:
            if admin.status == enums.ChatMemberStatus.OWNER: creator = admin
            elif admin.user.is_bot: bots.append(admin)
            else: admins.append(admin)
        if creator:
            text += f"\n\n🥀 ᴏᴡɴᴇʀ :\n<code> • </code>{creator.user.mention}"
            if creator.custom_title: text += f"\n<code> ┗━ {html.escape(creator.custom_title)}</code>"
        if admins:
            text += "\n\n💫 ᴀᴅᴍɪɴs :"
            for a in admins:
                text += f"\n<code> • </code>{a.user.mention}"
                if a.custom_title: text += f" | <code>{html.escape(a.custom_title)}</code>"
        if bots:
            text += "\n\n🤖 ʙᴏᴛs :"
            for b in bots: text += f"\n<code> • </code>{b.user.mention}"
        await msg.edit_text(text)
    except RPCError as e:
        await msg.edit_text(f"Error: {e.MESSAGE}")

__mod_name__ = "Admins"
__help__ = """
*User Commands*:
» /admins: List of admins in the chat
» /pinned: To get the current pinned message.

*Admins only:* 
» /promote: Promotes the user replied to
» /demote: Demotes the user replied to
» /title <title here>: Sets a custom title
» /admincache: Force refresh the admins list
» /setgtitle <text>: Set group title
» /setgpic: Reply to an image to set as group photo
» /delgpic: Delete group photo
» /setdesc: Set group description
» /setsticker: Set group sticker
» /pin: Silently pins the message
» /unpin: Unpins the currently pinned message
» /invitelink: Gets invitelink
"""
