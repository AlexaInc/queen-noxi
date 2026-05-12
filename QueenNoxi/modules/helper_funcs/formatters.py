import re
from typing import Optional, Dict, Tuple
from pyrogram import enums
from pyrogram.types import Message, User, Chat
from QueenNoxi import BOT_USERNAME
from QueenNoxi.modules.helper_funcs.string_handling import escape_markdown, escape_invalid_curly_brackets

async def format_message(text: str, user: User, chat: Chat) -> Tuple[str, Dict]:
    if not text:
        return "", {}

    first = escape_markdown(user.first_name)
    last = escape_markdown(user.last_name or user.first_name)
    fullname = escape_markdown(f"{user.first_name} {user.last_name}" if user.last_name else user.first_name)
    username = f"@{user.username}" if user.username else user.mention
    mention = user.mention
    id = user.id
    chatname = escape_markdown(chat.title if chat and chat.type != enums.ChatType.PRIVATE else user.first_name)
    
    rules_link = f"t.me/{BOT_USERNAME}?start={chat.id}" if chat and chat.type != enums.ChatType.PRIVATE else f"t.me/{BOT_USERNAME}"
    rules = f"[Rules]({rules_link})"

    VALID_PLACEHOLDERS = [
        "first", "last", "fullname", "username", "mention", "id", "chatname", "rules"
    ]
    
    text = escape_invalid_curly_brackets(text, VALID_PLACEHOLDERS)

    try:
        text = text.format(
            first=first,
            last=last,
            fullname=fullname,
            username=username,
            mention=mention,
            id=id,
            chatname=chatname,
            rules=rules
        )
    except Exception as e:
        import logging
        logging.error(f"Error formatting message: {e}")

    # Flags extraction
    flags = {
        "disable_web_page_preview": False,
        "disable_notification": False,
        "protect_content": False,
        "has_spoiler": False
    }

    if "{preview}" in text:
        text = text.replace("{preview}", "")
        flags["disable_web_page_preview"] = False # Logic might be inverted depending on default
    else:
        flags["disable_web_page_preview"] = True # Default to disable if not specified? 
        # Actually user said "{preview} enables link previews", so default should be disabled.
    
    if "{nonotif}" in text:
        text = text.replace("{nonotif}", "")
        flags["disable_notification"] = True
        
    if "{protect}" in text:
        text = text.replace("{protect}", "")
        flags["protect_content"] = True
        
    if "{mediaspoiler}" in text:
        text = text.replace("{mediaspoiler}", "")
        flags["has_spoiler"] = True

    return text.strip(), flags
