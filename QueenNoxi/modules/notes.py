import html
import re
from typing import Optional

from pyrogram import filters, Client, enums
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from pyrogram.errors import RPCError

import QueenNoxi.modules.sql.notes_sql as sql
from QueenNoxi import DRAGONS, pbot, BOT_ID, SUPPORT_CHAT
from QueenNoxi import DRAGONS, pbot, BOT_ID, SUPPORT_CHAT, LOGGER
from QueenNoxi.modules.disable import DisableAbleCommandHandler
from QueenNoxi.modules.helper_funcs.chat_status import connection_status, user_admin
from QueenNoxi.modules.helper_funcs.misc import build_keyboard, revert_buttons
from QueenNoxi.modules.helper_funcs.msg_types import get_note_type, Types
from QueenNoxi.modules.helper_funcs.string_handling import (
    escape_invalid_curly_brackets,
    escape_markdown
)
from QueenNoxi.modules.helper_funcs.formatters import format_message

# Do not async
@connection_status
async def get(client: Client, message: Message, notename: str, show_none=True, no_format=False, query=None):
    chat_id = message.chat.id
    note = sql.get_note(chat_id, notename)

    if note:
        reply_id = message.reply_to_message.id if message.reply_to_message else message.id

        if note.is_reply:
            try:
                await client.copy_message(chat_id, chat_id, int(note.value), reply_to_message_id=reply_id)
                return
            except RPCError:
                if query:
                    await query.answer("This message seems to have been lost.", show_alert=True)
                else:
                    await message.reply_text("This message seems to have been lost.")
                sql.rm_note(chat_id, notename)
                return
        
        res, flags = await format_message(note.value, message.from_user, message.chat)
        text = res

        buttons = sql.get_buttons(chat_id, notename)
        keyb = []
        parse_mode = enums.ParseMode.MARKDOWN
        
        if no_format:
            parse_mode = None
            text += revert_buttons(buttons)
        else:
            keyb = build_keyboard(buttons, notename=notename)

        keyboard = InlineKeyboardMarkup(keyb) if keyb else None

        try:
            if query and note.msgtype in (Types.BUTTON_TEXT, Types.TEXT):
                edit_flags = flags.copy()
                # Remove keys not supported by edit_message_text
                for key in ["disable_notification", "protect_content", "has_spoiler"]:
                    edit_flags.pop(key, None)
                
                await query.edit_message_text(
                    text,
                    parse_mode=parse_mode,
                    reply_markup=keyboard,
                    **edit_flags
                )
                return

            if note.msgtype in (Types.BUTTON_TEXT, Types.TEXT):
                flags.pop("has_spoiler", None)
                await message.reply_text(
                    text,
                    reply_to_message_id=reply_id,
                    parse_mode=parse_mode,
                    reply_markup=keyboard,
                    **flags
                )
            elif note.msgtype == Types.STICKER:
                await client.send_sticker(chat_id, note.file, reply_to_message_id=reply_id, reply_markup=keyboard, **flags)
            elif note.msgtype == Types.DOCUMENT:
                await client.send_document(chat_id, note.file, caption=text, reply_to_message_id=reply_id, parse_mode=parse_mode, reply_markup=keyboard, **flags)
            elif note.msgtype == Types.PHOTO:
                await client.send_photo(chat_id, note.file, caption=text, reply_to_message_id=reply_id, parse_mode=parse_mode, reply_markup=keyboard, **flags)
            elif note.msgtype == Types.AUDIO:
                await client.send_audio(chat_id, note.file, caption=text, reply_to_message_id=reply_id, parse_mode=parse_mode, reply_markup=keyboard, **flags)
            elif note.msgtype == Types.VOICE:
                await client.send_voice(chat_id, note.file, caption=text, reply_to_message_id=reply_id, parse_mode=parse_mode, reply_markup=keyboard, **flags)
            elif note.msgtype == Types.VIDEO:
                await client.send_video(chat_id, note.file, caption=text, reply_to_message_id=reply_id, parse_mode=parse_mode, reply_markup=keyboard, **flags)
            elif note.msgtype == Types.VIDEO_NOTE:
                await client.send_video_note(chat_id, note.file, reply_to_message_id=reply_id, reply_markup=keyboard, **flags)

        except RPCError as e:
            if query:
                await query.answer(f"Error: {e.MESSAGE}", show_alert=True)
            else:
                await message.reply_text(f"This note could not be sent. Error: {e.MESSAGE}")
            LOGGER.error(f"Could not send note {notename} in {chat_id}: {e}")
    elif show_none:
        if query:
            await query.answer("This note doesn't exist", show_alert=True)
        else:
            await message.reply_text("This note doesn't exist")


@pbot.on_message(filters.command("get") & filters.group)
@connection_status
async def cmd_get(client: Client, message: Message):
    args = message.command[1:]
    if len(args) >= 2 and args[1].lower() == "noformat":
        await get(client, message, args[0].lower(), show_none=True, no_format=True)
    elif len(args) >= 1:
        await get(client, message, args[0].lower(), show_none=True)
    else:
        await message.reply_text("Please specify a note name to get.")


@pbot.on_message(filters.regex(r"^#[^\s]+") & filters.group)
@connection_status
async def hash_get(client: Client, message: Message):
    no_hash = message.text[1:].lower().split()[0]
    await get(client, message, no_hash, show_none=False)


@pbot.on_message(filters.command("save") & filters.group)
@user_admin
@connection_status
async def save(client: Client, message: Message):
    chat_id = message.chat.id
    raw_text = message.text or message.caption
    entities = message.entities or message.caption_entities or []
    
    # Check if it's a reply
    if message.reply_to_message:
        replied = message.reply_to_message
        content_text = replied.text or replied.caption or ""
        content_entities = replied.entities or replied.caption_entities or []
        
        # Note name comes from the command args
        args = message.command[1:]
        note_name = args[0].lower() if args else None
        
        # Check for tags in replied message
        # Note name comes from the command args
        super_note_pattern = r"<([a-zA-Z0-9_-]+)>(.*?)</\1>"
        
        # Convert the ENTIRE replied message to markdown first
        from QueenNoxi.modules.helper_funcs.string_handling import markdown_parser, button_markdown_parser
        full_markdown = markdown_parser(content_text, content_entities)
        
        matches = list(re.finditer(super_note_pattern, full_markdown, re.DOTALL))
        
        if matches:
            saved = []
            for i, match in enumerate(matches):
                name = match.group(1).lower()
                inner_markdown = match.group(2).strip()
                
                # Parse buttons from the already-markdownified inner text
                t, b = button_markdown_parser(inner_markdown)
                
                sql.add_note_to_db(chat_id, name, t, Types.BUTTON_TEXT if b else Types.TEXT, buttons=b)
                saved.append(name)
                
                if i == 0 and note_name:
                    sql.add_note_to_db(chat_id, note_name, t, Types.BUTTON_TEXT if b else Types.TEXT, buttons=b)
                    if note_name != name:
                        saved.append(note_name)
            
            await message.reply_text(f"Saved {len(saved)} super-notes from reply: {', '.join(saved)}")
            return
        
        if not note_name:
            await message.reply_text("Specify a note name to save the reply!")
            return
            
        # No tags, save the whole replied message
        from QueenNoxi.modules.helper_funcs.string_handling import button_markdown_parser
        t, b = button_markdown_parser(content_text, entities=content_entities)
        
        # Handle media
        if replied.sticker:
            sql.add_note_to_db(chat_id, note_name, t, Types.STICKER, file=replied.sticker.file_id, buttons=b)
        elif replied.document:
            sql.add_note_to_db(chat_id, note_name, t, Types.DOCUMENT, file=replied.document.file_id, buttons=b)
        elif replied.photo:
            sql.add_note_to_db(chat_id, note_name, t, Types.PHOTO, file=replied.photo.file_id, buttons=b)
        elif replied.audio:
            sql.add_note_to_db(chat_id, note_name, t, Types.AUDIO, file=replied.audio.file_id, buttons=b)
        elif replied.voice:
            sql.add_note_to_db(chat_id, note_name, t, Types.VOICE, file=replied.voice.file_id, buttons=b)
        elif replied.video:
            sql.add_note_to_db(chat_id, note_name, t, Types.VIDEO, file=replied.video.file_id, buttons=b)
        else:
            sql.add_note_to_db(chat_id, note_name, t, Types.BUTTON_TEXT if b else Types.TEXT, buttons=b)
            
        await message.reply_text(f"Yas! Added note `{note_name}` from reply.")
        return

    # Non-reply case (legacy support for /save name content)
    super_note_pattern = r"<([a-zA-Z0-9_-]+)>(.*?)</\1>"
    
    first_space = raw_text.find(" ")
    if first_space == -1:
        await message.reply_text("Specify a note name or reply to a message!")
        return
    
    content_to_parse = raw_text[first_space+1:]
    # Convert the whole command text to markdown first
    from QueenNoxi.modules.helper_funcs.string_handling import markdown_parser, button_markdown_parser
    full_markdown = markdown_parser(raw_text, entities)
    
    matches = list(re.finditer(super_note_pattern, full_markdown, re.DOTALL))

    if matches:
        saved = []
        for i, match in enumerate(matches):
            name = match.group(1).lower()
            inner_markdown = match.group(2).strip()
            
            t, b = button_markdown_parser(inner_markdown)
            
            sql.add_note_to_db(chat_id, name, t, Types.BUTTON_TEXT if b else Types.TEXT, buttons=b)
            saved.append(name)

            if i == 0:
                args = raw_text.split()
                if len(args) >= 2:
                    cmd_note_name = args[1].lower()
                    if cmd_note_name != name:
                        sql.add_note_to_db(chat_id, cmd_note_name, t, Types.BUTTON_TEXT if b else Types.TEXT, buttons=b)
                        saved.append(cmd_note_name)
            
        await message.reply_text(f"Saved {len(saved)} super-notes: {', '.join(saved)}")
        return

    note_name, text, data_type, content, buttons = await get_note_type(message)
    if not note_name:
        await message.reply_text("Dude, you need to specify a note name!")
        return
        
    note_name = note_name.lower()
    if data_type is None:
        await message.reply_text("Dude, there's no note content!")
        return

    sql.add_note_to_db(chat_id, note_name, text, data_type, buttons=buttons, file=content)
    await message.reply_text(
        f"Yas! Added `{note_name}`.\nGet it with /get `{note_name}`, or `#{note_name}`",
        parse_mode=enums.ParseMode.MARKDOWN,
    )


@pbot.on_message(filters.command("clear") & filters.group)
@user_admin
@connection_status
async def clear(client: Client, message: Message):
    args = message.command[1:]
    chat_id = message.chat.id
    if len(args) >= 1:
        notename = args[0].lower()
        if sql.rm_note(chat_id, notename):
            await message.reply_text("Successfully removed note.")
        else:
            await message.reply_text("That's not a note in my database!")


@pbot.on_message(filters.command("removeallnotes") & filters.group)
async def clearall(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    member = await chat.get_member(user.id)
    if member.status != enums.ChatMemberStatus.OWNER:
        await message.reply_text("Only the chat owner can clear all notes at once.")
        return

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="Delete all notes", callback_data="notes_rmall")],
            [InlineKeyboardButton(text="Cancel", callback_data="notes_cancel")],
        ]
    )
    await message.reply_text(
        f"Are you sure you would like to clear ALL notes in {chat.title}? This action cannot be undone.",
        reply_markup=buttons,
    )


@pbot.on_callback_query(filters.regex(r"notes_.*"))
async def clearall_btn(client: Client, query):
    chat = query.message.chat
    member = await chat.get_member(query.from_user.id)
    if query.data == "notes_rmall":
        if member.status == enums.ChatMemberStatus.OWNER or query.from_user.id in DRAGONS:
            note_list = sql.get_all_chat_notes(chat.id)
            for note in note_list:
                sql.rm_note(chat.id, note.name.lower())
            await query.message.edit_text("Deleted all notes.")
        else:
            await query.answer("Only the owner of the chat can do this.", show_alert=True)
    elif query.data == "notes_cancel":
        if member.status == enums.ChatMemberStatus.OWNER or query.from_user.id in DRAGONS:
            await query.message.edit_text("Clearing of all notes has been cancelled.")
        else:
            await query.answer("Only the owner of the chat can do this.", show_alert=True)

@pbot.on_callback_query(filters.regex(r"^note_.*"))
async def note_callback(client: Client, query):
    notename = query.data.split("_", 1)[1]
    await get(client, query.message, notename, show_none=False, query=query)
    await query.answer()

@pbot.on_callback_query(filters.regex(r"^page_(next|prev|home)"))
async def paginate_callback(client: Client, query):
    data = query.data.split(":")
    action = data[0]
    current_note = data[1] if len(data) > 1 else None
    chat_id = query.message.chat.id

    # Get all notes in the chat sorted alphabetically to determine prev/next
    all_notes = sql.get_all_chat_notes(chat_id)
    note_names = sorted([n.name.lower() for n in all_notes])

    if not note_names:
        await query.answer("No notes found in this chat.", show_alert=True)
        return

    if action == "page_home":
        target = note_names[0]
    elif current_note and current_note in note_names:
        idx = note_names.index(current_note)
        if action == "page_next":
            target = note_names[(idx + 1) % len(note_names)]
        else:  # page_prev
            target = note_names[(idx - 1) % len(note_names)]
    else:
        # Fallback if no current_note or not in list
        target = note_names[0]

    if target:
        await get(client, query.message, target, show_none=False, query=query)
    await query.answer()


@DisableAbleCommandHandler(["notes", "saved"])
@connection_status
async def list_notes(client: Client, message: Message):
    chat_id = message.chat.id
    note_list = sql.get_all_chat_notes(chat_id)
    if not note_list:
        await message.reply_text("No notes in this chat!")
        return

    msg = "Get note by `#notename` \n\n  *ID*    *Note* \n"
    for i, note in enumerate(note_list, 1):
        note_name = f"`{i:2}.`  `#{(note.name.lower())}`\n"
        if len(msg) + len(note_name) > 4096:
            await message.reply_text(msg, parse_mode=enums.ParseMode.MARKDOWN)
            msg = ""
        msg += note_name

    if msg:
        await message.reply_text(msg, parse_mode=enums.ParseMode.MARKDOWN)


__mod_name__ = "Notes"
__help__ = """
 ❍ `/get <notename>`: get the note with this notename
 ❍ `#<notename>`: same as /get
 ❍ `/notes` or `/saved`: list all saved notes in this chat
 ❍ `/save <notename> <notedata>`: saves notedata as a note with name notename
 ❍ `/save <notename>`: save the replied message as a note with name notename
 ❍ `/clear <notename>`: clear note with this name
 ❍ `/removeallnotes`: removes all notes from the group
"""
