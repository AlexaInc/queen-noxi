from typing import Optional
from pyrogram import filters, Client
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from pyrogram.errors import BadRequest

import QueenNoxi.modules.sql.rules_sql as sql
from QueenNoxi import pbot, BOT_USERNAME
from QueenNoxi.modules.helper_funcs.chat_status import connection_status, user_admin
from QueenNoxi.modules.helper_funcs.string_handling import markdown_parser

@connection_status
async def get_rules(client: Client, message: Message):
    args = message.command
    here = len(args) > 1 and args[1] == "here"
    chat_id = message.chat.id
    
    rules = sql.get_rules(chat_id)
    if not rules:
        await message.reply_text("The group admins haven't set any rules for this chat yet.")
        return

    if here or message.chat.type == message.chat.type.PRIVATE:
        await message.reply_text(
            f"The rules for **{message.chat.title}** are:\n\n{rules}",
            disable_web_page_preview=True,
        )
    else:
        await message.reply_text(
            "ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ʀᴜʟᴇs.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="• ʀᴜʟᴇs •",
                            url=f"t.me/{BOT_USERNAME}?start={chat_id}",
                        ),
                    ],
                ],
            ),
        )

@connection_status
@user_admin
async def set_rules(client: Client, message: Message):
    chat_id = message.chat.id
    raw_text = message.text
    args = raw_text.split(None, 1)
    
    txt = None
    if len(args) == 2:
        txt = args[1]
    elif message.reply_to_message:
        txt = message.reply_to_message.text

    if txt:
        # Offset calculation for markdown parser
        offset = len(raw_text) - len(txt)
        markdown_rules = await markdown_parser(txt, message.entities, offset)
        sql.set_rules(chat_id, markdown_rules)
        await message.reply_text("Successfully set rules for this group.")
    else:
        await message.reply_text("There's... no rules?")

@connection_status
@user_admin
async def clear_rules(client: Client, message: Message):
    chat_id = message.chat.id
    sql.set_rules(chat_id, "")
    await message.reply_text("Successfully cleared rules!")

def __stats__():
    return f"• {sql.num_chats()} ɢʀᴏᴜᴘs ʜᴀᴠᴇ ʀᴜʟᴇs."

def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)

def __chat_settings__(chat_id, user_id):
    return f"This chat has had it's rules set: `{bool(sql.get_rules(chat_id))}`"

__help__ = """
 ‣ `/rules`*:* get the rules for this chat.
 ‣ `/rules here`*:* get the rules for this chat but send it in the chat.
*Admins only:*
  ‣ `/setrules <your rules here>`*:* set the rules for this chat.
  ‣ `/clearrules` or `/remrules`: clear the rules for this chat.
"""

__mod_name__ = "Rᴜʟᴇs"

@pbot.on_message(filters.command("rules") & (filters.group | filters.private))
async def get_rules_handler(client, message):
    await get_rules(client, message)

@pbot.on_message(filters.command("setrules") & filters.group)
async def set_rules_handler(client, message):
    await set_rules(client, message)

@pbot.on_message(filters.command(["clearrules", "remrules"]) & filters.group)
async def clear_rules_handler(client, message):
    await clear_rules(client, message)
