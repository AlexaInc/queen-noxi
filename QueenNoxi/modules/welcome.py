import html
import random
import re
import time
import asyncio
from pyrogram import filters, Client, enums
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ChatPermissions
)
from pyrogram.errors import RPCError

import QueenNoxi
import QueenNoxi.modules.sql.welcome_sql as sql
from QueenNoxi import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    EVENT_LOGS,
    LOGGER,
    OWNER_IDS,
    TIGERS,
    WOLVES,
    pbot,
    BOT_ID
)
from QueenNoxi.modules.helper_funcs.chat_status import (
    is_user_ban_protected,
    user_admin,
    bot_admin,
    can_restrict,
    connection_status
)
from QueenNoxi.modules.helper_funcs.misc import build_keyboard, revert_buttons
from QueenNoxi.modules.helper_funcs.msg_types import get_welcome_type, Types
from QueenNoxi.modules.helper_funcs.string_handling import (
    escape_invalid_curly_brackets,
    markdown_parser,
)
from QueenNoxi.modules.helper_funcs.formatters import format_message
from QueenNoxi.modules.log_channel import loggable
from QueenNoxi.modules.sql.global_bans_sql import is_user_gbanned

VALID_WELCOME_FORMATTERS = [
    "first",
    "last",
    "fullname",
    "username",
    "id",
    "count",
    "chatname",
    "mention",
]

# Verified user waitlist (for captcha)
VERIFIED_USER_WAITLIST = {}

async def send(message: Message, text: str, keyboard: InlineKeyboardMarkup, backup_message: str):
    chat = message.chat
    cleanserv = sql.clean_service(chat.id)
    reply_to = message.id if not cleanserv else None

    if cleanserv:
        try:
            await message.delete()
        except RPCError:
            pass

    try:
        return await message.reply_text(
            text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
            reply_to_message_id=reply_to
        )
    except RPCError as excp:
        LOGGER.error(f"Error sending welcome: {excp}")
        return await message.reply_text(backup_message, reply_to_message_id=reply_to)

@pbot.on_message(filters.new_chat_members & filters.group)
@loggable
async def new_member(client: Client, message: Message):
    chat = message.chat
    new_members = message.new_chat_members

    should_welc, cust_welcome, cust_content, welc_type = sql.get_welc_pref(chat.id)
    welc_mutes = sql.welcome_mutes(chat.id)

    for new_mem in new_members:
        if new_mem.id == BOT_ID:
            # Bot joined a new chat
            try:
                await client.send_message(
                    EVENT_LOGS,
                    f"#NEW_GROUP\n**Group Name:** {html.escape(chat.title)}\n**Chat ID:** `{chat.id}`"
                )
            except Exception as e:
                LOGGER.warning(f"Could not send new group log to EVENT_LOGS: {e}")
            await message.reply_text("Watashi ga kita!")
            continue

        if is_user_gbanned(new_mem.id):
            await client.ban_chat_member(chat.id, new_mem.id)
            continue

        # Special welcomes for devs/sudos etc.
        if new_mem.id in OWNER_IDS:
             await message.reply_text("The King has arrived!")
             continue
        elif new_mem.id in DEV_USERS:
             await message.reply_text("One of my creators joined!")
             continue

        if should_welc:
            buttons = sql.get_welc_buttons(chat.id)
            if cust_welcome:
                if cust_welcome == sql.DEFAULT_WELCOME:
                    cust_welcome = random.choice(sql.DEFAULT_WELCOME_MESSAGES)
                
                # Robust notename lookup for pagination
                _page_notename = ""
                if buttons and any(getattr(b, "url", "") in ("btn_next", "btn_back", "btn_home") for b in buttons):
                    import QueenNoxi.modules.sql.notes_sql as _nsql
                    _all_notes = _nsql.get_all_chat_notes(chat.id)
                    import re as _re
                    def _strip_html(data):
                        return _re.sub(r"<.*?>", "", str(data)).strip()
                    _content_raw = _strip_html(cust_welcome)
                    for _n in _all_notes:
                        if _strip_html(_n.value) == _content_raw:
                            _page_notename = _n.name.lower()
                            break
                
                keyb = build_keyboard(buttons, notename=_page_notename)
                keyboard = InlineKeyboardMarkup(keyb)
                
                res, flags = await format_message(cust_welcome, new_mem, chat)
            else:
                res, flags = await format_message(random.choice(sql.DEFAULT_WELCOME_MESSAGES), new_mem, chat)
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

            if welc_type in (Types.TEXT, Types.BUTTON_TEXT):
                # Text replies don't support has_spoiler
                text_flags = {k: v for k, v in flags.items() if k != "has_spoiler"}
                sent = await message.reply_text(
                    res,
                    reply_markup=keyboard,
                    reply_to_message_id=message.id if not sql.clean_service(chat.id) else None,
                    parse_mode=enums.ParseMode.HTML,
                    **text_flags
                )
            else:
                # Media DOES NOT support disable_web_page_preview
                media_flags = {k: v for k, v in flags.items() if k != "disable_web_page_preview"}
                
                # Check photo/video for spoiler support
                if welc_type not in (Types.PHOTO, Types.VIDEO):
                    media_flags.pop("has_spoiler", None)

                # Handle media welcomes
                sent = await client.send_cached_media(
                    chat.id,
                    cust_content,
                    caption=res,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML,
                    **media_flags
                )

            # Clean previous welcome
            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    await client.delete_messages(chat.id, prev_welc)
                except RPCError:
                    pass
            if sent:
                sql.set_clean_welcome(chat.id, sent.id)

        # Handle Welcome Mutes (Captcha)
        if welc_mutes and not await is_user_ban_protected(chat, new_mem.id):
            if welc_mutes == "soft":
                await chat.restrict_member(new_mem.id, ChatPermissions(can_send_messages=True, can_send_media_messages=False))
            elif welc_mutes == "strong":
                 # Implementation of captcha button
                 pass

@pbot.on_message(filters.left_chat_member & filters.group)
async def left_member(client: Client, message: Message):
    chat = message.chat
    user = message.left_chat_member

    if user.id == BOT_ID:
        return

    should_goodbye, cust_goodbye, leave_type = sql.get_gdbye_pref(chat.id)
    if should_goodbye:
        buttons = sql.get_gdbye_buttons(chat.id)
        
        # Robust notename lookup for pagination
        _page_notename = ""
        if buttons and any(getattr(b, "url", "") in ("btn_next", "btn_back", "btn_home") for b in buttons):
            import QueenNoxi.modules.sql.notes_sql as _nsql
            _all_notes = _nsql.get_all_chat_notes(chat.id)
            import re as _re
            def _strip_html(data):
                return _re.sub(r"<.*?>", "", str(data)).strip()
            _content_raw = _strip_html(cust_goodbye)
            for _n in _all_notes:
                if _strip_html(_n.value) == _content_raw:
                    _page_notename = _n.name.lower()
                    break
        
        keyb = build_keyboard(buttons, notename=_page_notename)
        keyboard = InlineKeyboardMarkup(keyb) if keyb else None
        
        # Format the message (supports all placeholders and tags)
        res, flags = await format_message(cust_goodbye, user, chat)
        if not res:
            res = f"Goodbye {user.first_name}!"
            
        if leave_type in (Types.TEXT, Types.BUTTON_TEXT):
            text_flags = {k: v for k, v in flags.items() if k != "has_spoiler"}
            await message.reply_text(
                res,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML,
                **text_flags
            )
        else:
            # Handle media goodbyes
            # Media DOES NOT support disable_web_page_preview
            media_flags = {k: v for k, v in flags.items() if k != "disable_web_page_preview"}
            if leave_type not in (Types.PHOTO, Types.VIDEO):
                media_flags.pop("has_spoiler", None)
            
            # Fetch content (file_id) stored in DB for media goodbye
            welc_settings = sql.SESSION.query(sql.Welcome).get(str(chat.id))
            content = welc_settings.custom_content if welc_settings else None
            sql.SESSION.close()
            
            if content:
                await client.send_cached_media(
                    chat.id,
                    content,
                    caption=res,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML,
                    **media_flags
                )
            else:
                await message.reply_text(res, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML, **flags)

@pbot.on_message(filters.command("welcome") & filters.group)
@user_admin
async def welcome(client: Client, message: Message):
    args = message.command[1:]
    chat = message.chat
    
    if not args:
        pref, _, _, _ = sql.get_welc_pref(chat.id)
        await message.reply_text(f"Welcome preference is set to: `{pref}`")
        return

    if args[0].lower() in ("on", "yes"):
        sql.set_welc_preference(chat.id, True)
        await message.reply_text("I'll greet members when they join!")
    elif args[0].lower() in ("off", "no"):
        sql.set_welc_preference(chat.id, False)
        await message.reply_text("I'll stop welcoming people.")

@pbot.on_message(filters.command("setwelcome") & filters.group)
@user_admin
async def set_welcome_msg(client: Client, message: Message):
    chat = message.chat
    
    # Check if it's a reply and extract media for super-welcome support
    if message.reply_to_message:
        replied = message.reply_to_message
        content_text = replied.text or replied.caption or ""
        content_entities = replied.entities or replied.caption_entities or []
        
        # Super-Welcome Parsing
        from pyrogram.parser.utils import add_surrogates
        surrogated_text = add_surrogates(content_text)
        
        super_filt_pattern = r"<(p[0-9]+|[a-zA-Z0-9_-]{2,})>(.*?)</\1>"
        matches = list(re.finditer(super_filt_pattern, surrogated_text, re.DOTALL))
        
        if matches:
            from QueenNoxi.modules.helper_funcs.string_handling import content_to_html, button_markdown_parser
            import QueenNoxi.modules.sql.notes_sql as note_sql
            
            # Extract media info to apply to ALL pages
            m_sticker = bool(replied.sticker)
            m_document = bool(replied.document)
            m_image = bool(replied.photo)
            m_audio = bool(replied.audio)
            m_voice = bool(replied.voice)
            m_video = bool(replied.video)
            m_gif = bool(replied.animation)
            
            _media = (replied.sticker or replied.document or replied.photo or replied.audio or replied.voice or replied.video or replied.animation)
            m_file = _media.file_id if _media else None
            
            replied_type = None
            if m_sticker: replied_type = Types.STICKER
            elif m_document: replied_type = Types.DOCUMENT
            elif m_image: replied_type = Types.PHOTO
            elif m_audio: replied_type = Types.AUDIO
            elif m_voice: replied_type = Types.VOICE
            elif m_video: replied_type = Types.VIDEO
            elif m_gif: replied_type = Types.ANIMATION
            
            saved_notes = []
            for i, match in enumerate(matches):
                keyword = match.group(1).lower()
                raw_inner = match.group(2)
                
                inner_text = raw_inner.strip()
                lead_strip = len(raw_inner) - len(raw_inner.lstrip())
                
                abs_start = match.start(2) + lead_strip
                abs_end   = abs_start + len(inner_text)
                
                segment_entities = []
                for ent in content_entities:
                    if ent.offset >= abs_start and (ent.offset + ent.length) <= abs_end:
                        import copy
                        new_ent = copy.copy(ent)
                        new_ent.offset -= abs_start
                        segment_entities.append(new_ent)
                
                from pyrogram.parser.utils import remove_surrogates
                html_text = remove_surrogates(content_to_html(inner_text, segment_entities))
                t, b = button_markdown_parser(html_text, is_html=True)
                
                # Save tags as NOTES
                current_type = replied_type or (Types.BUTTON_TEXT if b else Types.TEXT)
                note_sql.add_note_to_db(chat.id, keyword, t, current_type, file=m_file, buttons=b)
                saved_notes.append(keyword)

                # Set the first tag as the welcome
                if i == 0:
                    sql.set_custom_welcome(chat.id, m_file, t, current_type, b)
            
            await message.reply_text(f"Successfully set your welcome message!\nDetected and saved {len(matches)} tags as notes: {', '.join(saved_notes)}")
            return

    # Non-super handling
    text, data_type, content, buttons = await get_welcome_type(message)

    if not data_type:
        await message.reply_text("You didn't specify what to reply with!")
        return

    sql.set_custom_welcome(chat.id, content, text, data_type, buttons)
    await message.reply_text("Successfully set custom welcome message!")

@pbot.on_message(filters.command("goodbye") & filters.group)
@user_admin
async def goodbye(client: Client, message: Message):
    args = message.command[1:]
    chat = message.chat
    
    if not args:
        pref, _, _ = sql.get_gdbye_pref(chat.id)
        await message.reply_text(f"Goodbye preference is set to: `{pref}`")
        return

    if args[0].lower() in ("on", "yes"):
        sql.set_gdbye_preference(chat.id, True)
        await message.reply_text("I'll say goodbye when members leave!")
    elif args[0].lower() in ("off", "no"):
        sql.set_gdbye_preference(chat.id, False)
        await message.reply_text("I'll stop saying goodbye.")

@pbot.on_message(filters.command("setgoodbye") & filters.group)
@user_admin
async def set_goodbye_msg(client: Client, message: Message):
    chat = message.chat
    
    # Check if it's a reply and extract media for super-goodbye support
    if message.reply_to_message:
        replied = message.reply_to_message
        content_text = replied.text or replied.caption or ""
        content_entities = replied.entities or replied.caption_entities or []
        
        from pyrogram.parser.utils import add_surrogates
        surrogated_text = add_surrogates(content_text)
        
        super_filt_pattern = r"<(p[0-9]+|[a-zA-Z0-9_-]{2,})>(.*?)</\1>"
        matches = list(re.finditer(super_filt_pattern, surrogated_text, re.DOTALL))
        
        if matches:
            from QueenNoxi.modules.helper_funcs.string_handling import content_to_html, button_markdown_parser
            import QueenNoxi.modules.sql.notes_sql as note_sql
            
            # Extract media info
            _media = (replied.sticker or replied.document or replied.photo or replied.audio or replied.voice or replied.video or replied.animation)
            m_file = _media.file_id if _media else None
            
            replied_type = None
            if replied.sticker: replied_type = Types.STICKER
            elif replied.document: replied_type = Types.DOCUMENT
            elif replied.photo: replied_type = Types.PHOTO
            elif replied.audio: replied_type = Types.AUDIO
            elif replied.voice: replied_type = Types.VOICE
            elif replied.video: replied_type = Types.VIDEO
            elif replied.animation: replied_type = Types.ANIMATION
            
            saved_notes = []
            for i, match in enumerate(matches):
                keyword = match.group(1).lower()
                raw_inner = match.group(2)
                
                inner_text = raw_inner.strip()
                lead_strip = len(raw_inner) - len(raw_inner.lstrip())
                
                abs_start = match.start(2) + lead_strip
                abs_end   = abs_start + len(inner_text)
                
                segment_entities = []
                for ent in content_entities:
                    if ent.offset >= abs_start and (ent.offset + ent.length) <= abs_end:
                        import copy
                        new_ent = copy.copy(ent)
                        new_ent.offset -= abs_start
                        segment_entities.append(new_ent)
                
                from pyrogram.parser.utils import remove_surrogates
                html_text = remove_surrogates(content_to_html(inner_text, segment_entities))
                t, b = button_markdown_parser(html_text, is_html=True)
                
                current_type = replied_type or (Types.BUTTON_TEXT if b else Types.TEXT)
                note_sql.add_note_to_db(chat.id, keyword, t, current_type, file=m_file, buttons=b)
                saved_notes.append(keyword)

                if i == 0:
                    sql.set_custom_gdbye(chat.id, t, current_type, b, m_file)
            
            await message.reply_text(f"Successfully set your goodbye message!\nDetected and saved {len(matches)} tags as notes: {', '.join(saved_notes)}")
            return

    text, data_type, content, buttons = await get_welcome_type(message)

    if not data_type:
        await message.reply_text("You didn't specify what to reply with!")
        return

    sql.set_custom_gdbye(chat.id, text, data_type, buttons, content)
    await message.reply_text("Successfully set custom goodbye message!")

@pbot.on_message(filters.command("resetwelcome") & filters.group)
@user_admin
async def reset_welcome(client: Client, message: Message):
    chat = message.chat
    sql.set_custom_welcome(chat.id, None, sql.DEFAULT_WELCOME, Types.TEXT)
    await message.reply_text("Successfully reset welcome message to default!")

@pbot.on_message(filters.command("resetgoodbye") & filters.group)
@user_admin
async def reset_goodbye(client: Client, message: Message):
    chat = message.chat
    sql.set_custom_gdbye(chat.id, sql.DEFAULT_GOODBYE, Types.TEXT)
    await message.reply_text("Successfully reset goodbye message to default!")

@pbot.on_message(filters.command("cleanservice") & filters.group)
@user_admin
async def cleanservice(client: Client, message: Message):
    args = message.command[1:]
    chat = message.chat
    if not args:
        pref = sql.clean_service(chat.id)
        await message.reply_text(f"Clean service is currently: `{pref}`")
        return
    
    if args[0].lower() in ("on", "yes"):
        sql.set_clean_service(chat.id, True)
        await message.reply_text("I will now clean service messages!")
    else:
        sql.set_clean_service(chat.id, False)
        await message.reply_text("I will no longer clean service messages.")

__mod_name__ = "Welcome"
__help__ = """
Manage welcome and goodbye messages in your group.

**Commands:**
• `/welcome <on/off>`: Toggle greetings
• `/setwelcome <msg>`: Set custom welcome
• `/resetwelcome`: Reset welcome
• `/goodbye <on/off>`: Toggle goodbye messages
• `/setgoodbye <msg>`: Set custom goodbye
• `/resetgoodbye`: Reset goodbye
• `/cleanservice <on/off>`: Clean join/leave messages
"""
