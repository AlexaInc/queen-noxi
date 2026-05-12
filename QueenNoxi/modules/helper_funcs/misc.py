from math import ceil
from typing import Dict, List
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from QueenNoxi import NO_LOAD, pbot

class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text

def split_message(msg: str) -> List[str]:
    if len(msg) < 4096:
        return [msg]

    lines = msg.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < 4096:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line
    else:
        result.append(small_msg)

    return result

def paginate_modules(page_n: int, module_dict: Dict, prefix, chat=None) -> List:
    if not chat:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({})".format(
                        prefix, x.__mod_name__.lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )
    else:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({},{})".format(
                        prefix, chat, x.__mod_name__.lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )

    pairs = [modules[i * 3 : (i + 1) * 3] for i in range((len(modules) + 3 - 1) // 3)]

    round_num = len(modules) / 3
    calc = len(modules) - round(round_num)
    if calc in [1, 2]:
        pairs.append((modules[-1],))

    max_num_pages = ceil(len(pairs) / 4)
    modulo_page = page_n % max_num_pages

    if len(pairs) > 3:
        pairs = pairs[modulo_page * 6: 6* (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton(
                    "◁", callback_data="{}_prev({})".format(prefix, modulo_page)
                ),
                EqInlineKeyboardButton(
                    "• ʜᴏᴍᴇ •", callback_data="queennoxi_back"
                ),
                EqInlineKeyboardButton(
                    "▷", callback_data="{}_next({})".format(prefix, modulo_page)
                ),
            )
        ]
    else:
        pairs += [[EqInlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="queennoxi_back")]]

    return pairs

async def send_to_list(client, send_to: list, message: str, parse_mode=None) -> None:
    for user_id in set(send_to):
        try:
            await client.send_message(user_id, message, parse_mode=parse_mode)
        except Exception:
            pass

def build_keyboard(buttons):
    keyb = []
    for btn in buttons:
        color_prefix = ""
        if btn.color:
            if btn.color == "success":
                color_prefix = "🟢 "
            elif btn.color == "danger":
                color_prefix = "🔴 "
            elif btn.color == "primary":
                color_prefix = "🔵 "
            elif btn.color == "warning":
                color_prefix = "🟡 "
        
        btn_text = f"{color_prefix}{btn.name}"
        
        if btn.url.startswith("#"):
            note_name = btn.url[1:]
            button = InlineKeyboardButton(btn_text, callback_data=f"note_{note_name}")
        elif btn.url in ("btn_next", "btn_back", "btn_home"):
            button = InlineKeyboardButton(btn_text, callback_data=f"paginate_{btn.url}")
        else:
            button = InlineKeyboardButton(btn_text, url=btn.url)

        if btn.same_line and keyb:
            keyb[-1].append(button)
        else:
            keyb.append([button])
    return keyb

def revert_buttons(buttons):
    res = ""
    for btn in buttons:
        color_part = f"#{btn.color}" if btn.color else ""
        same_line = ":same" if btn.same_line else ""
        res += f"\n[{btn.name}](buttonurl{color_part}://{btn.url}{same_line})"
    return res

def is_module_loaded(name):
    return name not in NO_LOAD
