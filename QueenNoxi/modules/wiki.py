import wikipedia
import html
import os
from pyrogram import filters, Client, enums
from pyrogram.types import Message
from wikipedia.exceptions import DisambiguationError, PageError

from QueenNoxi import pbot
from QueenNoxi.modules.disable import DisableAbleCommandHandler

@pbot.on_message(filters.command("wiki"))
async def wiki(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Please provide logic for what to search on Wikipedia!")
        return

    search = message.text.split(None, 1)[1]
    try:
        res = wikipedia.summary(search)
    except DisambiguationError as e:
        await message.reply_text(
            f"Disambiguated pages found! Adjust your query accordingly.\n<i>{e}</i>",
            parse_mode=enums.ParseMode.HTML,
        )
        return
    except PageError as e:
        await message.reply_text(
            f"<code>{e}</code>", parse_mode=enums.ParseMode.HTML
        )
        return
    except Exception as e:
        await message.reply_text(f"Error: {e}")
        return

    if res:
        result = f"<b>{html.escape(search)}</b>\n\n"
        result += f"<i>{html.escape(res)}</i>\n"
        result += f"""<a href="https://en.wikipedia.org/wiki/{search.replace(" ", "%20")}">Read more...</a>"""
        
        if len(result) > 4000:
            file_path = f"wiki_{message.from_user.id}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result)
            await message.reply_document(file_path, caption="Result is too long, sending as file.")
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            await message.reply_text(
                result, 
                parse_mode=enums.ParseMode.HTML, 
                disable_web_page_preview=True
            )

__help__ = """
» /wiki (text) : Search about the given text on Wikipedia.
"""
__mod_name__ = "Wiki"
