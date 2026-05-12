import re
import time
from typing import List, Tuple
import bleach
import markdown2
from pyrogram import enums
from pyrogram.types import MessageEntity

MATCH_MD = re.compile(
    r"\*(.*?)\*|"
    r"_(.*?)_|"
    r"`(.*?)`|"
    r"(?<!\\)(\[.*?\])(\(.*?\))|"
    r"(?P<esc>[*_`\[])"
)

LINK_REGEX = re.compile(r"(?<!\\)\[.+?\]\((.*?)\)")
BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\(buttonurl(?:#([^:]+))?://(/{0,2})(.+?)(:same)?\))")

def _selective_escape(to_parse: str) -> str:
    offset = 0
    # Escape markdown-sensitive characters that aren't part of a valid formatting block
    for match in MATCH_MD.finditer(to_parse):
        if match.group("esc"):
            ent_start = match.start()
            to_parse = to_parse[: ent_start + offset] + "\\" + to_parse[ent_start + offset :]
            offset += 1
    return to_parse

def utf16_to_char(text: str, utf16_off: int) -> int:
    """Converts a UTF-16 offset into a Python character index."""
    if not text:
        return 0
    char_idx = 0
    utf16_idx = 0
    while utf16_idx < utf16_off and char_idx < len(text):
        # Surrogate pairs take 2 UTF-16 units but are 1 character in Python
        if ord(text[char_idx]) > 0xFFFF:
            utf16_idx += 2
        else:
            utf16_idx += 1
        char_idx += 1
    return char_idx

def markdown_parser(txt: str, entities: List[MessageEntity] = None, offset: int = 0) -> str:
    if not entities:
        return _selective_escape(txt)
    
    # Pre-calculate char offsets because ent.offset is in UTF-16 (Bot API standard)
    # but Python slices use char indices.
    sorted_entities = sorted(entities, key=lambda e: e.offset)
    
    prev = 0
    res = ""
    for ent in sorted_entities:
        start_char = utf16_to_char(txt, ent.offset)
        end_char = utf16_to_char(txt, ent.offset + ent.length)
        
        # Check clipping/alignment
        if start_char < 0:
            continue
            
        ent_text = txt[start_char:end_char]

        if ent.type == enums.MessageEntityType.BOLD:
            res += _selective_escape(txt[prev:start_char]) + "**" + ent_text + "**"
        elif ent.type == enums.MessageEntityType.ITALIC:
            res += _selective_escape(txt[prev:start_char]) + "__" + ent_text + "__"
        elif ent.type == enums.MessageEntityType.STRIKETHROUGH:
            res += _selective_escape(txt[prev:start_char]) + "~~" + ent_text + "~~"
        elif ent.type == enums.MessageEntityType.UNDERLINE:
            res += _selective_escape(txt[prev:start_char]) + "--" + ent_text + "--"
        elif ent.type == enums.MessageEntityType.SPOILER:
            res += _selective_escape(txt[prev:start_char]) + "||" + ent_text + "||"
        elif ent.type == enums.MessageEntityType.CUSTOM_EMOJI:
            res += _selective_escape(txt[prev:start_char]) + f"[{ent_text}](tg://emoji?id={ent.custom_emoji_id})"
        elif ent.type == enums.MessageEntityType.CODE:
            res += _selective_escape(txt[prev:start_char]) + "`" + ent_text + "`"
        elif ent.type == enums.MessageEntityType.PRE:
            res += _selective_escape(txt[prev:start_char]) + "```" + (ent.language or "") + "\n" + ent_text + "```"
        elif ent.type == enums.MessageEntityType.URL:
            if any(match.start(1) <= start_char and end_char <= match.end(1) for match in LINK_REGEX.finditer(txt)):
                continue
            else:
                res += _selective_escape(txt[prev:start_char]) + ent_text
        elif ent.type == enums.MessageEntityType.TEXT_LINK:
            res += _selective_escape(txt[prev:start_char]) + f"[{ent_text}]({ent.url})"
        elif ent.type == enums.MessageEntityType.MENTION:
            res += _selective_escape(txt[prev:start_char]) + ent_text
        elif ent.type == enums.MessageEntityType.TEXT_MENTION:
            res += _selective_escape(txt[prev:start_char]) + f"[{ent_text}](tg://user?id={ent.user.id})"
        else:
            res += _selective_escape(txt[prev:start_char]) + ent_text
        prev = end_char
    
    res += _selective_escape(txt[prev:])
    return res

class Button:
    def __init__(self, name, url, same_line=False, color=None):
        self.name = name
        self.url = url
        self.same_line = same_line
        self.color = color

def button_markdown_parser(txt: str, entities: List[MessageEntity] = None, offset: int = 0) -> Tuple[str, List[Button]]:
    markdown_note = markdown_parser(txt, entities, offset)
    prev = 0
    note_data = ""
    buttons = []
    for match in BTN_URL_REGEX.finditer(markdown_note):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and markdown_note[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:
            # match.group(2) -> name
            # match.group(3) -> color
            # match.group(5) -> url/back/next/home
            # match.group(6) -> :same
            buttons.append(Button(
                match.group(2),
                match.group(5),
                bool(match.group(6)),
                match.group(3)
            ))
            note_data += markdown_note[prev : match.start(1)]
            prev = match.end(1)
        else:
            note_data += markdown_note[prev : match.start(1) - 1]
            prev = match.start(1) - 1
    else:
        note_data += markdown_note[prev:]

    return note_data, buttons

def escape_invalid_curly_brackets(text: str, valids: List[str]) -> str:
    new_text = ""
    idx = 0
    while idx < len(text):
        if text[idx] == "{":
            if idx + 1 < len(text) and text[idx + 1] == "{":
                idx += 2
                new_text += "{{{{"
                continue
            else:
                success = False
                for v in valids:
                    if text[idx:].startswith("{" + v + "}"):
                        success = True
                        break
                if success:
                    new_text += text[idx : idx + len(v) + 2]
                    idx += len(v) + 2
                    continue
                else:
                    new_text += "{{"
        elif text[idx] == "}":
            if idx + 1 < len(text) and text[idx + 1] == "}":
                idx += 2
                new_text += "}}}}"
                continue
            else:
                new_text += "}}"
        else:
            new_text += text[idx]
        idx += 1
    return new_text

SMART_OPEN = "“"
SMART_CLOSE = "”"
START_CHAR = ("'", '"', SMART_OPEN)

def split_quotes(text: str) -> List:
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    key = remove_escapes(text[1:counter].strip())
    rest = text[counter + 1 :].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))

def remove_escapes(text: str) -> str:
    res = ""
    is_escaped = False
    for counter in range(len(text)):
        if is_escaped:
            res += text[counter]
            is_escaped = False
        elif text[counter] == "\\":
            is_escaped = True
        else:
            res += text[counter]
    return res

async def extract_time(message, time_val):
    if any(time_val.endswith(unit) for unit in ("m", "h", "d")):
        unit = time_val[-1]
        time_num = time_val[:-1]
        if not time_num.isdigit():
            await message.reply_text("Invalid time amount specified.")
            return None

        if unit == "m":
            return int(time.time() + int(time_num) * 60)
        elif unit == "h":
            return int(time.time() + int(time_num) * 60 * 60)
        elif unit == "d":
            return int(time.time() + int(time_num) * 24 * 60 * 60)
    else:
        await message.reply_text(f"Invalid time type specified. Expected m,h, or d, got: {time_val[-1]}")
        return None

def markdown_to_html(text):
    text = text.replace("*", "**").replace("`", "```").replace("~", "~~")
    _html = markdown2.markdown(text, extras=["strike", "underline"])
    return bleach.clean(_html, tags=["strong", "em", "a", "code", "pre", "strike", "u"], strip=True)[:-1]

def escape_markdown(text: str) -> str:
    return _selective_escape(text)
