import os
import zipfile
from pyrogram import filters
from QueenNoxi import pbot as app, TEMP_DOWNLOAD_DIRECTORY

async def check_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.privileges is not None
    except Exception:
        return False

@app.on_message(filters.command("zip"))
async def zip_cmd(_, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a file to compress it.")
    if message.chat.type.name != "PRIVATE":
        if not await check_admin(message.chat.id, message.from_user.id):
            return await message.reply("Hey, you are not admin. You can't use this command, But you can use in my PM 🙂")
    
    mone = await message.reply("⏳️ Please wait...")
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
        
    try:
        downloaded_file_name = await message.reply_to_message.download(TEMP_DOWNLOAD_DIRECTORY)
        directory_name = downloaded_file_name
        zipfile.ZipFile(directory_name + ".zip", "w", zipfile.ZIP_DEFLATED).write(directory_name)
        await message.reply_document(
            document=directory_name + ".zip",
            reply_to_message_id=message.id
        )
        os.remove(directory_name)
        os.remove(directory_name + ".zip")
        await mone.delete()
    except Exception as e:
        await mone.edit(str(e))


@app.on_message(filters.command("unzip"))
async def unzip_cmd(_, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a zip file.")
    if message.chat.type.name != "PRIVATE":
        if not await check_admin(message.chat.id, message.from_user.id):
            return await message.reply("Hey, You are not admin. You can't use this command, But you can use in my PM 🙂")

    mone = await message.reply("Processing...")
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
        
    extracted = TEMP_DOWNLOAD_DIRECTORY + "extracted/"
    if not os.path.isdir(extracted):
        os.makedirs(extracted)

    try:
        downloaded_file_name = await message.reply_to_message.download(TEMP_DOWNLOAD_DIRECTORY)
        with zipfile.ZipFile(downloaded_file_name, "r") as zip_ref:
            zip_ref.extractall(extracted)
            
        await mone.edit("Unzipping now 😌")
        
        def get_lst_of_files(input_directory, output_lst):
            for root, dirs, files in os.walk(input_directory):
                for file in files:
                    output_lst.append(os.path.join(root, file))
            return output_lst
            
        filename = sorted(get_lst_of_files(extracted, []))
        for single_file in filename:
            await app.send_document(
                message.chat.id,
                document=single_file,
                reply_to_message_id=message.id
            )
            os.remove(single_file)
        os.remove(downloaded_file_name)
        await mone.delete()
    except Exception as e:
        await mone.edit(str(e))

__help__ = """
ʜᴇʏ ɪ ᴄᴀɴ ᴄᴏɴᴠᴇʀᴛ ғɪʟᴇs ʜᴇʀᴇ..
 ❍ /zip *:* ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇʟᴇɢʀᴀᴍ ғɪʟᴇ ᴛᴏ ᴄᴏᴍᴘʀᴇss ɪᴛ ɪɴ .ᴢɪᴘ ғᴏʀᴍᴀᴛ
 ❍ /unzip *:* ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇʟᴇɢʀᴀᴍ ғɪʟᴇ ᴛᴏ ᴅᴇᴄᴏᴍᴘʀᴇss ɪᴛ ғʀᴏᴍ ᴛʜᴇ .ᴢɪᴘ ғᴏʀᴍᴀᴛ
"""

__mod_name__ = "Zɪᴘᴘᴇʀ​"
