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
    chat_id = message.chat.id
    raw_text = message.text or message.caption
    entities = message.entities or message.caption_entities or []
    
    # Check if it's a reply
    if message.reply_to_message:
        replied = message.reply_to_message
        content_text = replied.text or replied.caption or ""
        content_entities = replied.entities or replied.caption_entities or []
        
        args = message.command[1:]
        trigger = args[0].lower() if args else None
        
        # Super-Filter Parsing
        import re
        import re
        super_filt_pattern = r"<([a-zA-Z0-9_-]+)>(.*?)</\1>"
        
        from QueenNoxi.modules.helper_funcs.string_handling import markdown_parser, button_markdown_parser
        full_markdown = markdown_parser(content_text, content_entities)
        
        matches = list(re.finditer(super_filt_pattern, full_markdown, re.DOTALL))
        
        if matches:
            import QueenNoxi.modules.sql.notes_sql as note_sql
            saved_notes = []
            for i, match in enumerate(matches):
                keyword = match.group(1).lower()
                inner_markdown = match.group(2).strip()
                
                t, b = button_markdown_parser(inner_markdown)
                
                # Save tags as NOTES
                note_sql.add_note_to_db(chat_id, keyword, t, Types.BUTTON_TEXT if b else Types.TEXT, buttons=b)
                saved_notes.append(keyword)

                # Point primary trigger to first tag's content
                if i == 0 and trigger:
                    sql.add_filter(chat_id, trigger, t, buttons=b)
                    if trigger != keyword:
                        saved_notes.append(f"{trigger} (filter)")
            
            await message.reply_text(f"Saved {len(matches)} tags as notes. Trigger `{trigger}` set to Page 1.")
            return
        
        if not trigger:
            await message.reply_text("Specify a trigger name to save the reply!")
            return
            
        # No tags, save the whole replied message
        from QueenNoxi.modules.helper_funcs.string_handling import button_markdown_parser
        t, b = button_markdown_parser(content_text, entities=content_entities)
        
        # Handle media filters
        if replied.sticker:
            sql.add_filter(chat_id, trigger, t, is_sticker=True, buttons=b)
        elif replied.document:
            sql.add_filter(chat_id, trigger, t, is_document=True, buttons=b)
        elif replied.photo:
            sql.add_filter(chat_id, trigger, t, is_image=True, buttons=b)
        elif replied.audio:
            sql.add_filter(chat_id, trigger, t, is_audio=True, buttons=b)
        elif replied.voice:
            sql.add_filter(chat_id, trigger, t, is_voice=True, buttons=b)
        elif replied.video:
            sql.add_filter(chat_id, trigger, t, is_video=True, buttons=b)
        else:
            sql.add_filter(chat_id, trigger, t, buttons=b)
            
        await message.reply_text(f"Yas! Added filter `{trigger}` from reply.")
        return

    # Non-reply case
    import re
    super_filt_pattern = r"<([a-zA-Z0-9_-]+)>(.*?)</\1>"
    
    first_space = raw_text.find(" ")
    if first_space != -1:
        from QueenNoxi.modules.helper_funcs.string_handling import markdown_parser, button_markdown_parser
        full_markdown = markdown_parser(raw_text, entities)
        matches = list(re.finditer(super_filt_pattern, full_markdown, re.DOTALL))
        
        if matches:
            import QueenNoxi.modules.sql.notes_sql as note_sql
            saved_notes = []
            for i, match in enumerate(matches):
                keyword = match.group(1).lower()
                inner_markdown = match.group(2).strip()
                
                t, b = button_markdown_parser(inner_markdown)
                
                # Save tags as NOTES
                note_sql.add_note_to_db(chat_id, keyword, t, Types.BUTTON_TEXT if b else Types.TEXT, buttons=b)
                saved_notes.append(keyword)

                # Point primary trigger from args if provided
                if i == 0:
                    args = raw_text.split()
                    if len(args) >= 2:
                        cmd_trigger = args[1].lower()
                        if cmd_trigger != keyword:
                            sql.add_filter(chat_id, cmd_trigger, t, buttons=b)
                            saved_notes.append(f"{cmd_trigger} (filter)")
            
            await message.reply_text(f"Saved {len(matches)} tags as notes. Trigger `{cmd_trigger}` set to Page 1.")
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
                flags.pop("has_spoiler", None) # Fix TypeError: Message.reply() got an unexpected keyword argument 'has_spoiler'
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
