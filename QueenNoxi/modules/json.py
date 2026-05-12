import io
from pyrogram import filters
from QueenNoxi import pbot as app

@app.on_message(filters.command("json"))
async def _(_, message):
    if getattr(message, "forward_from", None):
        return
    if message.chat.type.name != "PRIVATE":
        try:
            member = await app.get_chat_member(message.chat.id, message.from_user.id)
            if member.privileges is None:
                await message.reply("🥴 ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴩᴏᴡᴇʀ ᴛᴏ ᴜsᴇ ᴛʜɪs ɪɴ ɢʀᴏᴜᴩs, ʙᴜᴛ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ɪᴛ ɪɴ ᴍʏ ᴩᴍ.")
                return
        except Exception:
            return

    reply_to_id = message.reply_to_message.id if message.reply_to_message else message.id
    the_real_message = str(message.reply_to_message) if message.reply_to_message else str(message)
    
    if len(the_real_message) > 4095:
        with io.BytesIO(str.encode(the_real_message)) as out_file:
            out_file.name = "json.text"
            await app.send_document(
                message.chat.id,
                document=out_file,
                reply_to_message_id=reply_to_id,
            )
            await message.delete()
    else:
        await message.reply("`{}`".format(the_real_message))
