import html
import traceback
from pyrogram import filters, Client, enums
from pyrogram.types import Message

from QueenNoxi import pbot, DEV_USERS

@pbot.on_message(filters.command("errors"))
async def list_errors(client: Client, message: Message):
    if message.from_user.id not in DEV_USERS:
        return
    await message.reply_text("Error logging is being refactored for Pyrogram. Check logs for details.")

# Global error handling is typically done by wrapping the handler execution loop 
# or using custom middleware in newer Pyrogram versions, but for this migration 
# we'll rely on the standard logging for now.

__mod_name__ = "Errors"
