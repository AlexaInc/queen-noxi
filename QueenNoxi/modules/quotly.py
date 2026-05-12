import asyncio
import base64
import os
import aiohttp
import json
import io
from pyrogram import filters, enums
from pyrogram.types import Message
from pyrogram.errors import RPCError
from QueenNoxi import pbot, LOGGER, BOT_ID

# --- QUOTLY API CONFIG (Matching alexatg project) ---
API_URL = "https://quotlytga-quoteapi.hf.space/api/generate"

async def download_thumb(client, message: Message):
    """Select the best thumbnail based on JS reference priority"""
    try:
        media = message.photo or message.sticker or message.document or message.animation or message.video
        if not media:
            return None
        
        if message.sticker:
             if not (message.sticker.is_video or message.sticker.is_animated):
                 path = await client.download_media(message.sticker.file_id)
                 if path:
                     with open(path, "rb") as f: data = f.read()
                     os.remove(path)
                     return data

        if hasattr(media, "thumbs") and media.thumbs:
            priority = ['v', 'm', 'y', 'x', 'w', 's']
            thumb_to_download = None
            for p in priority:
                for thumb in media.thumbs:
                    if hasattr(thumb, "type") and thumb.type == p:
                        thumb_to_download = thumb
                        break
                if thumb_to_download: break
            if not thumb_to_download: thumb_to_download = media.thumbs[-1]
            path = await client.download_media(thumb_to_download.file_id)
            if path:
                with open(path, "rb") as f: data = f.read()
                os.remove(path)
                return data

        if message.photo:
            path = await client.download_media(message.photo.file_id)
            if path:
                with open(path, "rb") as f: data = f.read()
                os.remove(path)
                return data
    except Exception as e:
        LOGGER.warning(f"Thumb download failed: {e}")
    return None

async def get_avatar_b64(client, user_id):
    """Fetch avatar and return as Data URL (using avatarBase64 key in API)"""
    try:
        chat = await client.get_chat(user_id)
        if chat.photo:
            path = await client.download_media(chat.photo.small_file_id)
            if path:
                with open(path, "rb") as f: content = f.read()
                os.remove(path)
                return "data:image/png;base64," + base64.b64encode(content).decode()
    except Exception:
        pass
    return ""

def format_entities(entities):
    if not entities: return []
    res = []
    for ent in entities:
        ent_type = ent.type.name.lower()
        if ent_type == "text_mention": ent_type = "mention"
        elif ent_type == "strikethrough": ent_type = "strike"
        entry = {"type": ent_type, "offset": ent.offset, "length": ent.length}
        # Pass custom emoji document_id so the API can render premium emoji
        if ent_type == "custom_emoji" and hasattr(ent, "custom_emoji_id") and ent.custom_emoji_id:
            entry["document_id"] = ent.custom_emoji_id
        res.append(entry)
    return res

async def get_message_data(client, message: Message, include_reply=False):
    user = message.from_user or message.sender_chat
    user_id = user.id if user else 1
    
    if hasattr(user, "first_name"):
        first_name = user.first_name or "User"
        last_name = getattr(user, "last_name", "") or ""
    else:
        first_name = getattr(user, "title", "User")
        last_name = ""
    
    avatar_b64 = await get_avatar_b64(client, user_id)
    entities = format_entities(message.entities or message.caption_entities)
    media_data = await download_thumb(client, message)
    media_b64 = ("data:image/png;base64," + base64.b64encode(media_data).decode()) if media_data else None

    # Try to get emoji status (custom emoji on profile)
    emoji_status_id = None
    try:
        full_user = await client.get_users(user_id)
        if hasattr(full_user, "emoji_status") and full_user.emoji_status:
            emoji_status_id = getattr(full_user.emoji_status, "custom_emoji_id", None)
    except Exception:
        pass

    # schema strictly aligned with alexatg/generatequote2.js
    msg_data = {
        "id": str(user_id),
        "firstName": first_name,
        "lastName": last_name,
        "avatarBase64": avatar_b64,
        "message": message.text or message.caption or "",
        "nameColorId": user_id % 7,
        "entities": entities,
        "mediaBase64": media_b64,
        "isSticker": bool(media_b64 and not (message.text or message.caption)),
        "isAbsoluteLast": False
    }

    if emoji_status_id:
        msg_data["emojiStatusId"] = emoji_status_id
    
    if message.forward_origin:
        origin = message.forward_origin
        try:
             if origin.type == enums.MessageOriginType.USER:
                 u = origin.sender_user
                 msg_data["forwardName"] = f"{u.first_name} {u.last_name or ''}".strip()
             elif origin.type == enums.MessageOriginType.CHAT:
                 msg_data["forwardName"] = origin.sender_chat.title
             elif origin.type == enums.MessageOriginType.CHANNEL:
                 msg_data["forwardName"] = origin.chat.title
        except: pass

    if include_reply and message.reply_to_message:
        rep = message.reply_to_message
        rep_user = rep.from_user or rep.sender_chat
        msg_data["replySender"] = (rep_user.first_name if hasattr(rep_user, "first_name") else getattr(rep_user, "title", "User")) if rep_user else "User"
        msg_data["replyMessage"] = rep.text or rep.caption or (rep.sticker.emoji if rep.sticker else "Media")
        msg_data["replysendercolor"] = (rep_user.id if rep_user else 0) % 7

    return msg_data

async def generate_quote(messages, background_color="#1b1429"):
    payload = {
        "type": "quote",
        "format": "webp",
        "backgroundColor": background_color,
        "width": 512,
        "height": 768,
        "scale": 2,
        "messages": messages
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, json=payload, timeout=60) as resp:
                if resp.status == 200:
                    content_type = resp.headers.get("Content-Type", "")
                    if "image" in content_type:
                        return await resp.read()
                    data = await resp.json()
                    if data.get("ok"):
                        return base64.b64decode(data["result"]["image"])
                    elif "result" in data and "image" in data["result"]:
                         return base64.b64decode(data["result"]["image"])
        except Exception as e:
            LOGGER.error(f"Generate Quote Error: {e}")
    return None

@pbot.on_message(filters.command(["q", "quote"]))
async def quotly(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message with `/q` to create a quote sticker.")

    args = message.text.split()[1:]
    count = 1
    include_reply = "r" in [a.lower() for a in args]
    for arg in args:
        if arg.isdigit(): count = min(20, max(1, int(arg)))

    processing = await message.reply_text("<code>Generating quote sticker...</code>")
    messages_to_quote = []
    
    try:
        start_id = message.reply_to_message.id
        msg_ids = [start_id + i for i in range(count)]
        fetched = await client.get_messages(message.chat.id, msg_ids)
        if not isinstance(fetched, list): fetched = [fetched]
            
        for msg in fetched:
            if msg and not msg.empty:
                if msg.text and msg.text.startswith("/") and len(fetched) > 1: continue
                data = await get_message_data(client, msg, include_reply if msg.id == start_id else False)
                messages_to_quote.append(data)
                
        if not messages_to_quote:
             return await processing.edit_text("Could not fetch messages.")

        messages_to_quote[-1]["isAbsoluteLast"] = True
        quote_content = await generate_quote(messages_to_quote)
        
        # Automatic fallback without images if API fails
        if not quote_content and any(m.get("avatarBase64") or m.get("mediaBase64") for m in messages_to_quote):
            LOGGER.info("Quotly failed with images, retrying text-only...")
            for m in messages_to_quote:
                m["avatarBase64"] = ""
                m["mediaBase64"] = None
            quote_content = await generate_quote(messages_to_quote)

        if quote_content:
            await processing.delete()
            sticker = io.BytesIO(quote_content)
            sticker.name = "quote.webp"
            if count >= 6: 
                await message.reply_document(sticker, caption="Quote generated!")
            else:
                await message.reply_sticker(sticker)
        else:
            await processing.edit_text("Failed to generate quote. The API might be down.")
            
    except Exception as e:
        LOGGER.exception(f"Quotly Command Error: {e}")
        await processing.edit_text("Something went wrong.")

__mod_name__ = "Quotly"
