from functools import wraps
from pyrogram import enums
from pyrogram.types import Message

async def send_message(message: Message, text: str, *args, **kwargs):
    try:
        return await message.reply_text(text, *args, **kwargs)
    except Exception as err:
        if "REPLY_MESSAGE_ID_INVALID" in str(err):
            return await message.reply_text(text, quote=False, *args, **kwargs)


def typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    async def command_func(client, message, *args, **kwargs):
        await client.send_chat_action(
            chat_id=message.chat.id, action=enums.ChatAction.TYPING
        )
        return await func(client, message, *args, **kwargs)

    return command_func
