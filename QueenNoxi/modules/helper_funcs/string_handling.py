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

from pyrogram.parser.markdown import Markdown

def _selective_escape(to_parse: str) -> str:
    offset = 0
    # Escape markdown-sensitive characters that aren't part of a valid formatting block
    for match in MATCH_MD.finditer(to_parse):
        if match.group("esc"):
            ent_start = match.start()
            to_parse = to_parse[: ent_start + offset] + "\\" + to_parse[ent_start + offset :]
            offset += 1
    return to_parse

def markdown_parser(txt: str, entities: List[MessageEntity] = None, offset: int = 0) -> str:
    if not entities:
        return _selective_escape(txt)
    
    # Use Pyrogram's native markdown unparser.
    # It handles UTF-16 surrogate pairs and entity alignment perfectly.
    try:
        # We need to ensure we don't pass a Message object instead of a string
        text_str = str(txt)
        return Markdown(None).unparse(text_str, entities)
    except Exception:
        # Fallback to selective escape if unparse fails for any reason
        return _selective_escape(txt)

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
