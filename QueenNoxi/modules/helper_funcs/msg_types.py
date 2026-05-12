from enum import IntEnum, unique
from pyrogram.types import Message
from QueenNoxi.modules.helper_funcs.string_handling import button_markdown_parser

@unique
class Types(IntEnum):
    TEXT = 0
    BUTTON_TEXT = 1
    STICKER = 2
    DOCUMENT = 3
    PHOTO = 4
    AUDIO = 5
    VOICE = 6
    VIDEO = 7
    VIDEO_NOTE = 8
    ANIMATION = 9

async def get_note_type(msg: Message):
    data_type = None
    content = None
    text = ""
    raw_text = msg.text or msg.caption
    args = raw_text.split(None, 2)
    if len(args) < 2:
        return None, None, None, None, []

    note_name = args[1]
    buttons = []

    if len(args) >= 3:
        offset = 0 # In Pyrogram, entities offsets start from 0 relative to the text they are in
        text, buttons = button_markdown_parser(
            args[2],
            entities=msg.entities or msg.caption_entities,
            offset=offset,
        )
        data_type = Types.BUTTON_TEXT if buttons else Types.TEXT

    elif msg.reply_to_message:
        reply = msg.reply_to_message
        msgtext = reply.text or reply.caption or ""
        entities = reply.entities or reply.caption_entities
        
        if reply.text or reply.caption:
            text, buttons = button_markdown_parser(msgtext, entities=entities)
            data_type = Types.BUTTON_TEXT if buttons else Types.TEXT

        if reply.sticker:
            content = reply.sticker.file_id
            data_type = Types.STICKER
        elif reply.document:
            content = reply.document.file_id
            data_type = Types.DOCUMENT
        elif reply.photo:
            content = reply.photo.file_id
            data_type = Types.PHOTO
        elif reply.audio:
            content = reply.audio.file_id
            data_type = Types.AUDIO
        elif reply.voice:
            content = reply.voice.file_id
            data_type = Types.VOICE
        elif reply.video:
            content = reply.video.file_id
            data_type = Types.VIDEO
        elif reply.video_note:
            content = reply.video_note.file_id
            data_type = Types.VIDEO_NOTE
        elif reply.animation:
            content = reply.animation.file_id
            data_type = Types.ANIMATION

    return note_name, text, data_type, content, buttons

async def get_welcome_type(msg: Message):
    data_type = None
    content = None
    text = ""
    buttons = []

    reply = msg.reply_to_message
    if reply:
        if reply.sticker:
            content = reply.sticker.file_id
            data_type = Types.STICKER
        elif reply.document:
            content = reply.document.file_id
            text = reply.caption
            data_type = Types.DOCUMENT
        elif reply.photo:
            content = reply.photo.file_id
            text = reply.caption
            data_type = Types.PHOTO
        elif reply.audio:
            content = reply.audio.file_id
            text = reply.caption
            data_type = Types.AUDIO
        elif reply.voice:
            content = reply.voice.file_id
            text = reply.caption
            data_type = Types.VOICE
        elif reply.video:
            content = reply.video.file_id
            text = reply.caption
            data_type = Types.VIDEO
        elif reply.video_note:
            content = reply.video_note.file_id
            data_type = Types.VIDEO_NOTE
        
        msgtext = reply.text or reply.caption or ""
        entities = reply.entities or reply.caption_entities
        text, buttons = button_markdown_parser(msgtext, entities=entities)
    else:
        args = msg.text.split(None, 1)
        if len(args) >= 2:
            text, buttons = button_markdown_parser(args[1], entities=msg.entities)
    
    if not data_type:
        data_type = Types.BUTTON_TEXT if buttons else Types.TEXT if text else None

    return text, data_type, content, buttons

async def get_filter_type(msg: Message):
    text = None
    data_type = None
    content = None
    buttons = []

    if not msg.reply_to_message and msg.text and len(msg.text.split()) >= 3:
        raw_text = msg.text.split(None, 2)[2]
        text, buttons = button_markdown_parser(raw_text, entities=msg.entities)
        data_type = Types.BUTTON_TEXT if buttons else Types.TEXT

    elif msg.reply_to_message:
        reply = msg.reply_to_message
        if reply.text or reply.caption:
            msgtext = reply.text or reply.caption
            entities = reply.entities or reply.caption_entities
            text, buttons = button_markdown_parser(msgtext, entities=entities)
            
            # Auto-detect buttons from InlineKeyboardMarkup if no markdown buttons found
            if not buttons and reply.reply_markup and reply.reply_markup.inline_keyboard:
                from QueenNoxi.modules.helper_funcs.string_handling import Button
                for row in reply.reply_markup.inline_keyboard:
                    for btn in row:
                        url = btn.url or (f"#{btn.callback_data}" if btn.callback_data else "")
                        if url:
                            same = True if row.index(btn) > 0 else False
                            buttons.append(Button(btn.text, url, same_line=same))

            data_type = Types.BUTTON_TEXT if buttons else Types.TEXT
        
        if reply.sticker:
            content = reply.sticker.file_id
            data_type = Types.STICKER
        elif reply.document:
            content = reply.document.file_id
            data_type = Types.DOCUMENT
        elif reply.photo:
            content = reply.photo.file_id
            data_type = Types.PHOTO
        elif reply.audio:
            content = reply.audio.file_id
            data_type = Types.AUDIO
        elif reply.voice:
            content = reply.voice.file_id
            data_type = Types.VOICE
        elif reply.video:
            content = reply.video.file_id
            data_type = Types.VIDEO
        elif reply.video_note:
            content = reply.video_note.file_id
            data_type = Types.VIDEO_NOTE

    return text, data_type, content, buttons


##
