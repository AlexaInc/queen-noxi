import os
from datetime import datetime

from PIL import Image
from telegraph import Telegraph, exceptions, upload_file

from pyrogram import filters
from QueenNoxi import pbot as app

TMP_DOWNLOAD_DIRECTORY = "./"
telegraph = Telegraph(domain="graph.org")
r = telegraph.create_account(short_name="Controller")
auth_url = r["auth_url"]


@app.on_message(filters.command(["tgm", "tgt"]))
async def _(_, message):
    if getattr(message, "forward_from", None):
        return
    input_str = message.command[0].replace("tg", "")
    optional_title = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    
    if message.reply_to_message:
        start = datetime.now()
        r_message = message.reply_to_message
        
        if input_str == "m":
            downloaded_file_name = await r_message.download(TMP_DOWNLOAD_DIRECTORY)
            end = datetime.now()
            ms = (end - start).seconds
            h = await message.reply(f"Downloaded to {downloaded_file_name} in {ms} seconds.")
            
            if downloaded_file_name.endswith((".webp")):
                resize_image(downloaded_file_name)
            try:
                start = datetime.now()
                media_urls = upload_file(downloaded_file_name)
            except exceptions.TelegraphException as exc:
                await h.edit("ERROR: " + str(exc))
                os.remove(downloaded_file_name)
            else:
                end = datetime.now()
                (end - start).seconds
                os.remove(downloaded_file_name)
                await h.edit(
                    f"Uploaded to https://graph.org{media_urls[0]}",
                    disable_web_page_preview=False,
                )
                
        elif input_str == "t":
            title_of_page = r_message.from_user.first_name if r_message.from_user else "Unknown"
            if optional_title:
                title_of_page = optional_title
                
            page_content = r_message.text or r_message.caption or ""
            if r_message.media:
                if page_content != "":
                    title_of_page = page_content
                downloaded_file_name = await r_message.download(TMP_DOWNLOAD_DIRECTORY)
                m_list = None
                with open(downloaded_file_name, "rb") as fd:
                    m_list = fd.readlines()
                for m in m_list:
                    page_content += m.decode("UTF-8") + "\n"
                os.remove(downloaded_file_name)
                
            page_content = page_content.replace("\n", "<br>")
            response = telegraph.create_page(title_of_page, html_content=page_content)
            end = datetime.now()
            ms = (end - start).seconds
            await message.reply(
                f"Pasted to https://graph.org/{response['path']} in {ms} seconds.",
                disable_web_page_preview=False,
            )
    else:
        await message.reply("Reply to a message to get a permanent telegra.ph link.")


def resize_image(image):
    im = Image.open(image)
    im.save(image, "PNG")


__help__ = """
ɪ ᴄᴀɴ ᴜᴘʟᴏᴀᴅ ғɪʟᴇs ᴛᴏ ᴛᴇʟᴇɢʀᴀᴘʜ
 ❍ /tgm :ɢᴇᴛ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ ᴏғ ʀᴇᴘʟɪᴇᴅ ᴍᴇᴅɪᴀ
 ❍ /tgt :ɢᴇᴛ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ ᴏғ ʀᴇᴘʟɪᴇᴅ ᴛᴇxᴛ
 ❍ /tgt [ᴄᴜsᴛᴏᴍ ɴᴀᴍᴇ]: ɢᴇᴛ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ ᴏғ ʀᴇᴘʟɪᴇᴅ ᴛᴇxᴛ ᴡɪᴛʜ ᴄᴜsᴛᴏᴍ ɴᴀᴍᴇ.
"""

__mod_name__ = "T-Gʀᴀᴘʜ"
