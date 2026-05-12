import html
from pyrogram import filters, Client, enums
from pyrogram.types import Message

from QueenNoxi import pbot, DEV_USERS
from QueenNoxi.modules import ALL_MODULES

@pbot.on_message(filters.command("listmodules"))
async def list_modules(client: Client, message: Message):
    if message.from_user.id not in DEV_USERS:
        return
    
    module_list = "**Loaded Modules:**\n\n"
    for module in sorted(ALL_MODULES):
        module_list += f" • `{module}`\n"
    
    await message.reply_text(module_list)

__mod_name__ = "Modules"
__help__ = """
• `/listmodules`: List all loaded modules (Devs only).
"""
