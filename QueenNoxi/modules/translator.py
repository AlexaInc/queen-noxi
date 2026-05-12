import html
from gpytranslate import SyncTranslator
from pyrogram import filters, Client, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from QueenNoxi import pbot, BOT_NAME, BOT_USERNAME, OWNER_ID
from QueenNoxi.modules.disable import DisableAbleCommandHandler

trans = SyncTranslator()

@pbot.on_message(filters.command(["tr", "tl"]))
async def totranslate(client: Client, message: Message):
    reply_msg = message.reply_to_message
    if not reply_msg:
        await message.reply_text(
            "Reply to a message to translate it!\n"
            "Example: `/tr en-hi` or `/tr en`\n"
            "Click [here](https://t.me/queennoxibotzone/16) for language codes.",
            disable_web_page_preview=True,
        )
        return

    to_translate = reply_msg.text or reply_msg.caption
    if not to_translate:
        await message.reply_text("I can't translate that!")
        return

    try:
        args = message.command[1].lower() if len(message.command) > 1 else "en"
        if "-" in args:
            source, dest = args.split("-")
        else:
            source = trans.detect(to_translate)
            dest = args
    except:
        source = trans.detect(to_translate)
        dest = "en"

    translation = trans(to_translate, sourcelang=source, targetlang=dest)
    reply = (
        f"**Translated from {source} to {dest}**:\n"
        f"`{translation.text}`"
    )

    await message.reply_text(reply)

@pbot.on_message(filters.command(["repo", "source"]))
async def repo(client: Client, message: Message):
    me = await client.get_me()
    await message.reply_photo(
        photo="https://te.legra.ph/file/1a72f3770dcb90ee8b3f7.jpg",
        caption=f"""**Hey {message.from_user.mention},\n\nI am [{me.first_name}](https://t.me/{me.username})**

**» My Developer:** [QueenNoxi](tg://user?id={OWNER_ID})
**» Python Version:** `3.10`
**» Library:** `Pyrogram`

**Group Controller source is now public!**""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Owner", user_id=OWNER_ID)],
            [InlineKeyboardButton("Repo", url="https://github.com/Noob-QueenNoxi/QueenNoxi")]
        ])
    )

__help__ = """
• `/tr <lang>`: Translate replied message.
• `/repo`: Get bot source code.
"""
__mod_name__ = "Trans"
