import re
import html
import random
from pyrogram import filters, Client, enums
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from pyrogram.errors import RPCError

import QueenNoxi
from QueenNoxi import pbot, LOGGER, DRAGONS
from QueenNoxi.modules.helper_funcs.chat_status import user_admin, connection_status
from QueenNoxi.modules.helper_funcs.misc import build_keyboard, revert_buttons
from QueenNoxi.modules.helper_funcs.msg_types import get_filter_type, Types
from QueenNoxi.modules.helper_funcs.string_handling import button_markdown_parser, split_quotes
from QueenNoxi.modules.helper_funcs.formatters import format_message
from QueenNoxi.modules.sql import cust_filters_sql as sql

# Handler group for filters
HANDLER_GROUP = 10

@pbot.on_message(filters.command("filter") & filters.group)
@user_admin
@connection_status
async def add_filter(client: Client, message: Message):
    # Super-Filter Parsing
    import re
    super_filt_pattern = r"<([a-zA-Z0-9_-]+)>(.*?)</\1>"
    raw_text = message.text or message.caption
    
    # We want the text after the command
    first_space = raw_text.find(" ")
    if first_space != -1:
        content_to_parse = raw_text[first_space+1:]
        matches = list(re.finditer(super_filt_pattern, content_to_parse, re.DOTALL))
        
        if matches:
            from QueenNoxi.modules.helper_funcs.string_handling import button_markdown_parser
            entities = message.entities or message.caption_entities or []
            saved_filters = []
            for match in matches:
                keyword = match.group(1).lower()
                inner_text = match.group(2).strip()
                
                # Start and End indices in raw_text
                start_idx = first_space + 1 + match.start(2)
                end_idx = first_space + 1 + match.end(2)
                
                # Filter and shift entities
                segment_entities = []
                for ent in entities:
                    if ent.offset >= start_idx and (ent.offset + ent.length) <= end_idx:
                        import copy
                        new_ent = copy.copy(ent)
                        new_ent.offset -= start_idx
                        segment_entities.append(new_ent)
                
                t, b = button_markdown_parser(inner_text, entities=segment_entities)
                sql.add_filter(message.chat.id, keyword, t, buttons=b)
                saved_filters.append(keyword)
            
            await message.reply_text(f"Successfully saved {len(saved_filters)} filters: {', '.join(saved_filters)}")
            return

    # Extract keyword and content
    chat_id = message.chat.id
    args = message.text.split(None, 1)

    if len(args) < 2 and not message.reply_to_message:
        await message.reply_text("Please provide a keyword and reply text for the filter!")
        return

    if message.reply_to_message:
        if len(args) < 2:
            await message.reply_text("Please provide a keyword for this filter!")
            return
        keyword = args[1].lower()
    else:
        extracted = split_quotes(args[1])
        if len(extracted) < 2:
            await message.reply_text("Please provide both a keyword and a reply text!")
            return
        keyword = extracted[0].lower()

    text, file_type, file_id, buttons = await get_filter_type(message)
    
    if not file_type:
        await message.reply_text("You didn't specify what to reply with!")
        return

    sql.new_add_filter(chat_id, keyword, text, file_type, file_id, buttons)
    await message.reply_text(f"Saved filter '{keyword}'!")

@pbot.on_message(filters.command("stop") & filters.group)
@user_admin
@connection_status
async def stop_filter(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.command[1:]

    if not args:
        await message.reply_text("What filter should I stop?")
        return

    keyword = args[0].lower()
    if sql.remove_filter(chat_id, keyword):
        await message.reply_text(f"Stopped replying to '{keyword}'.")
    else:
        await message.reply_text("That's not an active filter!")

@pbot.on_message(filters.command("filters") & filters.group)
@connection_status
async def list_handlers(client: Client, message: Message):
    chat_id = message.chat.id
    all_handlers = sql.get_chat_triggers(chat_id)

    if not all_handlers:
        await message.reply_text("No filters saved in this chat!")
        return

    filter_list = f"**Filters in {html.escape(message.chat.title)}:**\n"
    for keyword in all_handlers:
        filter_list += f" • `{keyword}`\n"

    await message.reply_text(filter_list)

@pbot.on_message(filters.text & filters.group, group=HANDLER_GROUP)
async def reply_filter(client: Client, message: Message):
    if not message.text:
        return

    chat_id = message.chat.id
    chat_filters = sql.get_chat_triggers(chat_id)
    
    for keyword in chat_filters:
        pattern = rf"( |^|[^\w]){re.escape(keyword)}( |$|[^\w])"
        if re.search(pattern, message.text, flags=re.IGNORECASE):
            filt = sql.get_filter(chat_id, keyword)
            buttons = sql.get_buttons(chat_id, keyword)
            keyboard = InlineKeyboardMarkup(build_keyboard(buttons)) if buttons else None
            
            res, flags = await format_message(filt.reply_text, message.from_user, message.chat)

            if filt.file_type in (Types.TEXT, Types.BUTTON_TEXT):
                await message.reply_text(
                    res,
                    reply_markup=keyboard,
                    reply_to_message_id=message.id,
                    **flags
                )
            else:
                await client.send_cached_media(
                    chat_id,
                    filt.file_id,
                    caption=res,
                    reply_markup=keyboard,
                    reply_to_message_id=message.id,
                    **flags
                )
            break

__mod_name__ = "Filters"
__help__ = """
**Admin Commands:**
• `/filter <keyword> <reply>`: Add a filter
• `/stop <keyword>`: Stop a filter
• `/filters`: List all filters
• `/removeallfilters`: Stop ALL filters (Owner only)
"""
