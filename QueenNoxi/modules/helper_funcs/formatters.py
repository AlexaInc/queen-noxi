import re
from typing import Optional, Dict, Tuple
from pyrogram import enums
from pyrogram.types import Message, User, Chat
from QueenNoxi import BOT_USERNAME
from QueenNoxi.modules.helper_funcs.string_handling import html as html_handler, escape_invalid_curly_brackets
import html

async def format_message(text: str, user: User, chat: Chat) -> Tuple[str, Dict]:
    if not text:
        return "", {}

    first = html.escape(user.first_name)
    last = html.escape(user.last_name or user.first_name)
    fullname = html.escape(f"{user.first_name} {user.last_name}" if user.last_name else user.first_name)
    
    # Explicitly use HTML tag for mention/username to prevent raw markup issues
    mention_link = f'<a href="tg://user?id={user.id}">{first}</a>'
    
    username = f"@{user.username}" if user.username else mention_link
    mention = mention_link
    id = user.id
    chatname = html.escape(chat.title if chat and chat.type != enums.ChatType.PRIVATE else user.first_name)
    
    from QueenNoxi.modules.sql import rules_sql as r_sql
    rules_text = r_sql.get_rules(chat.id) if (chat and chat.type != enums.ChatType.PRIVATE) else ""
    rules = rules_text or "No rules set."

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
        flags["disable_web_page_preview"] = False  # {preview} = enable previews
    else:
        flags["disable_web_page_preview"] = True  # default: disable previews
    
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
