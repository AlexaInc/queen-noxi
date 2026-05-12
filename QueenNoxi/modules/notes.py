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
from QueenNoxi.modules.disable import DisableAbleCommandHandler
from QueenNoxi.modules.helper_funcs.chat_status import connection_status, user_admin
from QueenNoxi.modules.helper_funcs.misc import build_keyboard, revert_buttons
from QueenNoxi.modules.helper_funcs.msg_types import get_note_type, Types
from QueenNoxi.modules.helper_funcs.string_handling import (
    escape_invalid_curly_brackets,
    escape_markdown
)

# Do not async
@connection_status
async def get(client: Client, message: Message, notename: str, show_none=True, no_format=False):
    chat_id = message.chat.id
    note = sql.get_note(chat_id, notename)

    if note:
        reply_id = message.reply_to_message.id if message.reply_to_message else message.id

        if note.is_reply:
            # logic for forward_message - in Pyrogram we use message.forward() or client.copy_message()
            # but note.value stores message_id if is_reply was True in PTB version
            # We'll try copy_message
            try:
                await client.copy_message(chat_id, chat_id, int(note.value), reply_to_message_id=reply_id)
                return
            except RPCError:
                await message.reply_text("This message seems to have been lost.")
                sql.rm_note(chat_id, notename)
                return
        
        VALID_NOTE_FORMATTERS = [
            "first",
            "last",
            "fullname",
            "username",
            "id",
            "chatname",
            "mention",
        ]
        valid_format = escape_invalid_curly_brackets(note.value, VALID_NOTE_FORMATTERS)
        if valid_format:
            text = valid_format.format(
                first=escape_markdown(message.from_user.first_name),
                last=escape_markdown(message.from_user.last_name or message.from_user.first_name),
                fullname=escape_markdown(
                    " ".join(
                        [message.from_user.first_name, message.from_user.last_name]
                        if message.from_user.last_name
                        else [message.from_user.first_name]
                    )
                ),
                username="@" + message.from_user.username if message.from_user.username else message.from_user.mention,
                mention=message.from_user.mention,
                chatname=escape_markdown(message.chat.title if message.chat.type != enums.ChatType.PRIVATE else message.from_user.first_name),
                id=message.from_user.id,
            )
        else:
            text = ""

        buttons = sql.get_buttons(chat_id, notename)
        keyb = []
        parse_mode = enums.ParseMode.MARKDOWN
        
        if no_format:
            parse_mode = None
            text += revert_buttons(buttons)
        else:
            keyb = build_keyboard(buttons)

        keyboard = InlineKeyboardMarkup(keyb) if keyb else None

        try:
            if note.msgtype in (Types.BUTTON_TEXT, Types.TEXT):
                await message.reply_text(
                    text,
                    reply_to_message_id=reply_id,
                    parse_mode=parse_mode,
                    reply_markup=keyboard,
                )
            elif note.msgtype == Types.STICKER:
                await client.send_sticker(chat_id, note.file, reply_to_message_id=reply_id, reply_markup=keyboard)
            elif note.msgtype == Types.DOCUMENT:
                await client.send_document(chat_id, note.file, caption=text, reply_to_message_id=reply_id, parse_mode=parse_mode, reply_markup=keyboard)
            elif note.msgtype == Types.PHOTO:
                await client.send_photo(chat_id, note.file, caption=text, reply_to_message_id=reply_id, parse_mode=parse_mode, reply_markup=keyboard)
            elif note.msgtype == Types.AUDIO:
                await client.send_audio(chat_id, note.file, caption=text, reply_to_message_id=reply_id, parse_mode=parse_mode, reply_markup=keyboard)
            elif note.msgtype == Types.VOICE:
                await client.send_voice(chat_id, note.file, caption=text, reply_to_message_id=reply_id, parse_mode=parse_mode, reply_markup=keyboard)
            elif note.msgtype == Types.VIDEO:
                await client.send_video(chat_id, note.file, caption=text, reply_to_message_id=reply_id, parse_mode=parse_mode, reply_markup=keyboard)
            elif note.msgtype == Types.VIDEO_NOTE:
                await client.send_video_note(chat_id, note.file, reply_to_message_id=reply_id, reply_markup=keyboard)

        except RPCError as e:
            await message.reply_text(f"This note could not be sent. Error: {e.MESSAGE}")
            LOGGER.error(f"Could not send note {notename} in {chat_id}: {e}")
    elif show_none:
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
