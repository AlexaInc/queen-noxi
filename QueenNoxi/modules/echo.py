from pyrogram import filters
from pyrogram.types import Message
from QueenNoxi import pbot
from QueenNoxi.modules.helper_funcs.chat_status import sudo_plus

@pbot.on_message(filters.command("go"))
async def go_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /go <text>")
        return

    text = message.text.split(None, 1)[1]
    try:
        await message.delete()
    except Exception:
        pass
    if message.reply_to_message:
        await message.reply_to_message.reply_text(text)
    else:
        await client.send_message(message.chat.id, text)

@pbot.on_message(filters.command("more"))
@sudo_plus
async def more_cmd(client, message: Message):
    if len(message.command) < 3:
        await message.reply_text("Usage: /more <count> <text>")
        return
    
    args = message.text.split(None, 2)
    try:
        count = int(args[1])
    except ValueError:
        await message.reply_text("Count must be an integer.")
        return
    
    # Cap count to prevent spam/floodwaits
    count = min(count, 50)
    text = args[2]

    try:
        await message.delete()
    except Exception:
        pass

    for _ in range(count):
        if message.reply_to_message:
            await message.reply_to_message.reply_text(text)
        else:
            await client.send_message(message.chat.id, text)

__mod_name__ = "Echo"
__help__ = """
**Commands:**
• `/go <text>`: Delete your message and send text as the bot. (Available to all)

**Sudo/Owner restrict:**
• `/more <count> <text>`: Repeat text count times as the bot.
"""
