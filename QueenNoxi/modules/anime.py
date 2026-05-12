import json
import random
import aiohttp
from pyrogram import filters, Client, enums
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from QueenNoxi import pbot, OWNER_ID
from QueenNoxi.modules.disable import DisableAbleCommandHandler

QUOTES_IMG = [
    "https://i.imgur.com/Iub4RYj.jpg",
    "https://i.imgur.com/uvNMdIl.jpg",
    "https://i.imgur.com/YOBOntg.jpg",
    "https://i.imgur.com/fFpO2ZQ.jpg",
    "https://i.imgur.com/f0xZceK.jpg",
    "https://i.imgur.com/RlVcCip.jpg",
    "https://i.imgur.com/CjpqLRF.jpg",
    "https://i.imgur.com/8BHZDk6.jpg",
    "https://i.imgur.com/8bHeMgy.jpg",
    "https://i.imgur.com/5K3lMvr.jpg",
    "https://i.imgur.com/NTzw4RN.jpg",
    "https://i.imgur.com/wJxryAn.jpg",
    "https://i.imgur.com/9L0DWzC.jpg",
    "https://i.imgur.com/sBe8TTs.jpg",
    "https://i.imgur.com/1Au8gdf.jpg",
    "https://i.imgur.com/28hFQeU.jpg",
    "https://i.imgur.com/Qvc03JY.jpg",
    "https://i.imgur.com/gSX6Xlf.jpg",
    "https://i.imgur.com/iP26Hwa.jpg",
    "https://i.imgur.com/uSsJoX8.jpg",
    "https://i.imgur.com/OvX3oHB.jpg",
    "https://i.imgur.com/JMWuksm.jpg",
    "https://i.imgur.com/lhM3fib.jpg",
    "https://i.imgur.com/64IYKkw.jpg",
    "https://i.imgur.com/nMbyA3J.jpg",
    "https://i.imgur.com/7KFQhY3.jpg",
    "https://i.imgur.com/mlKb7zt.jpg",
    "https://i.imgur.com/JCQGJVw.jpg",
    "https://i.imgur.com/hSFYDEz.jpg",
    "https://i.imgur.com/PQRjAgl.jpg",
    "https://i.imgur.com/ot9624U.jpg",
    "https://i.imgur.com/iXmqN9y.jpg",
    "https://i.imgur.com/RhNBeGr.jpg",
    "https://i.imgur.com/tcMVNa8.jpg",
    "https://i.imgur.com/LrVg810.jpg",
    "https://i.imgur.com/TcWfQlz.jpg",
    "https://i.imgur.com/muAUdvJ.jpg",
    "https://i.imgur.com/AtC7ZRV.jpg",
    "https://i.imgur.com/sCObQCQ.jpg",
    "https://i.imgur.com/AJFDI1r.jpg",
    "https://i.imgur.com/TCgmRrH.jpg",
    "https://i.imgur.com/LMdmhJU.jpg",
    "https://i.imgur.com/eyyax0N.jpg",
    "https://i.imgur.com/YtYxV66.jpg",
    "https://i.imgur.com/289f9cebe37f31a943f98.jpg",
]

async def anime_quote():
    url = "https://animechan.vercel.app/api/random"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                dic = await response.json()
                return dic["quote"], dic["character"], dic["anime"]
    return "No quote found.", "Unknown", "Unknown"

@pbot.on_message(filters.command("quote"))
@DisableAbleCommandHandler("quote")
async def quotes(client: Client, message: Message):
    quote, character, anime = await anime_quote()
    msg = f"<i>❝{quote}❞</i>\n\n<b>{character} from {anime}</b>"
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Change🔁", callback_data="change_quote")]]
    )
    await message.reply_text(
        msg,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML,
    )

@pbot.on_callback_query(filters.regex(r"change_quote|quote_change"))
async def change_quote_btn(client: Client, query: CallbackQuery):
    quote, character, anime = await anime_quote()
    msg = f"<i>❝{quote}❞</i>\n\n<b>{character} from {anime}</b>"
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="ᴄʜᴀɴɢᴇ🔁", callback_data="quote_change")]]
    )
    try:
        await query.message.edit_text(msg, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    except:
        await query.answer("Error or same content.")

@pbot.on_message(filters.command("animequotes"))
@DisableAbleCommandHandler("animequotes")
async def animequotes_cmd(client: Client, message: Message):
    if message.reply_to_message:
        await message.reply_to_message.reply_photo(random.choice(QUOTES_IMG))
    else:
        await message.reply_photo(random.choice(QUOTES_IMG))

__mod_name__ = "Quotes"
__help__ = """
• `/quote`: Get a random anime quote.
• `/animequotes`: Get a random anime quote image.
"""
