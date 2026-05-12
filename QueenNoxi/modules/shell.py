import subprocess
import io
from pyrogram import filters, Client, enums
from pyrogram.types import Message

from QueenNoxi import LOGGER, pbot, OWNER_ID
from QueenNoxi.modules.helper_funcs.chat_status import dev_plus

@pbot.on_message(filters.command("sh") & filters.user(OWNER_ID))
@dev_plus
async def shell(client: Client, message: Message):
    cmd = message.text.split(None, 1)
    if len(cmd) == 1:
        await message.reply_text("No command to execute was given.")
        return
    
    cmd = cmd[1]
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    stdout, stderr = process.communicate()
    
    reply = ""
    stderr = stderr.decode()
    stdout = stdout.decode()
    
    if stdout:
        reply += f"**Stdout**\n`{stdout}`\n"
        LOGGER.info(f"Shell - {cmd} - {stdout}")
    if stderr:
        reply += f"**Stderr**\n`{stderr}`\n"
        LOGGER.error(f"Shell - {cmd} - {stderr}")
        
    if len(reply) > 4000:
        with io.BytesIO(str.encode(reply)) as out_file:
            out_file.name = "shell_output.txt"
            await message.reply_document(document=out_file, caption="Output too long, sent as file.")
    elif reply:
        await message.reply_text(reply, parse_mode=enums.ParseMode.MARKDOWN)
    else:
        await message.reply_text("Clean execution (No output)")

__mod_name__ = "Sʜᴇʟʟ"
__help__ = """
★ᴏᴡɴᴇʀ ᴄᴍᴅ ★
 ❍ /sh: ᴇxᴇᴄᴜᴛᴇ sʜᴇʟʟ ᴄᴏᴍᴍᴀɴᴅs
"""
