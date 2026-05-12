import asyncio
import aiohttp
import html
import os
import random
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, RPCError

from pyrogram.types import Message
from QueenNoxi import pbot, LOGGER
from QueenNoxi.config import Config
TENOR_API_KEY = Config.TENOR_API_KEY
DRAGONS = Config.DRAGONS
OWNER_IDS = Config.OWNER_IDS
SUDOERS = list(set(DRAGONS + OWNER_IDS))

import zipfile
import shutil
from QueenNoxi.modules.disable import DisableAbleCommandHandler


from QueenNoxi.modules.helper_funcs.chat_status import (
    user_admin, 
    bot_admin, 
    can_restrict, 
    user_can_ban
)

# ── Setup Caching ────────────────────────────────────────────────────────────
CACHE_DIR = "QueenNoxi/resources/animation_cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

async def get_random_gif(category: str):
    """Fetch a random GIF URL from Tenor or local cache."""
    tenor_map = {
        "kill": "kill", "love": "love", "hug": "hug", "slap": "slap",
        "pat": "pat", "kiss": "kiss", "brain": "think", "moon": "sleep",
        "hack": "hacker", "police": "police", "bombs": "explosion", "clock": "clock"
    }
    
    action = tenor_map.get(category, category)
    cat_dir = os.path.join(CACHE_DIR, category)
    if not os.path.exists(cat_dir):
        os.makedirs(cat_dir)

    # 1. Try Tenor API
    if TENOR_API_KEY:
        try:
            query = f"{action} anime".replace(" ", "%20")
            url = f"https://tenor.googleapis.com/v2/search?q={query}&key={TENOR_API_KEY}&limit=5&random=true"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('results'):
                            chosen = random.choice(data['results'])
                            gif_url = chosen['media_formats']['gif']['url']
                            
                            # Async Background Download for Cache (best effort)
                            asyncio.create_task(cache_gif(category, gif_url))
                            return gif_url
        except Exception as e:
            LOGGER.warning(f"Tenor API error for {category}: {e}")

    # 2. Fallback to Local Cache
    cached_files = [f for f in os.listdir(cat_dir) if f.endswith(".gif")]
    if cached_files:
        local_file = random.choice(cached_files)
        return os.path.join(cat_dir, local_file)
            
    return None

async def cache_gif(category: str, url: str):
    """Download and save a GIF to the local cache if it doesn't exist."""
    cat_dir = os.path.join(CACHE_DIR, category)
    # Limit cache size per category (e.g. 10 files)
    if len(os.listdir(cat_dir)) >= 15:
        return

    file_id = url.split("/")[-2] if "/" in url else str(random.randint(1000, 9999))
    file_path = os.path.join(cat_dir, f"{file_id}.gif")
    if os.path.exists(file_path):
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    with open(file_path, "wb") as f:
                        f.write(data)
    except Exception:
        pass








# ── Animation lists ───────────────────────────────────────────────────────────
brain_chain = [
    "🧠", "🧠💥", "💭🧠", "🤯", "🧠🔥", "💡🧠", "🤔🧠",
    "💥🧠💥", "🧠📤", "📤🗑️", "🗑️💨", "🧠❌", "🗑️", "✅"
]

clock_ani = [
    "🕛", "🕧", "🕐", "🕜", "🕑", "🕝", "🕒", "🕞", "🕓", "🕟", "🕔"
]

police_ani = [
    "🚓", "🚓💨", "🚔", "🚔💨", "🚨", "🚨🚨", "👮", "👮‍♂️🚓",
    "🚓🚨👮", "🚨🚨👮‍♂️", "👮‍♂️🔦"
]

moon_ani = [
    "🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘", "🌑", "🌒",
    "🌓", "🌔", "🌕", "🌖", "🌗", "🌘", "🌑", "🌒", "🌓", "🌔",
    "🌕", "🌕✨", "🌕🌟", "🌕💫", "🌕⭐", "🌕🌟✨", "🌔", "🌓",
    "🌒", "🌑", "🌙", "🌙✨"
]

bomb_ettu = [
    "💣", "💣💣", "💣💣💣", "💣💣💣💣", "💥", "💥💥", "💥💥💥", "🔥💥", "☠️"
]

hack_you = [
    "🖥️ Booting...", "🔍 Scanning target...", "🔓 Bypassing firewall...",
    "💻 Injecting payload...", "📡 Connecting...", "🔑 Cracking password...",
    "📂 Accessing files...", "📊 Downloading data...", "🗄️ Extracting...",
    "📤 Uploading backdoor...", "🔐 Locking access...", "🎭 Covering tracks...",
    "🧹 Cleaning logs...", "⚙️ Finalizing...", "✅ Access granted!",
    "📁 All data secured.", "🏴‍☠️ Mission complete.", "😎 You've been hacked!"
]

love_siren = [
    "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "❤️‍🔥",
    "💗", "💓", "💞", "💕", "💝", "💖", "💘", "💟", "❣️", "❤️",
    "💑", "👫", "💏", "💞", "💕❤️", "💖💖", "💗💗", "💓❤️💓",
    "❤️‍🔥❤️", "💘💘", "💞💞💞", "💖✨", "💝🌹", "🌹❤️", "True Love💞"
]

kill_you = [
    "🔫", "🔫💨", "😵", "😵‍💫", "💀", "⚰️🕯️", "🪦", "😱💀",
    "🔫😵", "💀☠️", "⚰️", "☠️"
]

slap_ani = ["Slapping...", "SLAP! 👋", "Ouch! 💥", "👋💥", "😵"]
pat_ani = ["Patting...", "Pat pat... ✨", "Good job! 💖", "✋✨", "😊"]
hug_ani = ["Hugging...", "HUG! 🤗", "Warm hugs! ❤️", "🫂❤️", "✨"]
kiss_ani = ["Kissing...", "KISS! 💋", "Muah! 💘", "😘💋", "🔥"]

ban_ani = [
    "🔨 Initializing BanHammer...", 
    "🔍 Locating target user...", 
    "⚖️ Applying punishment protocol...", 
    "⚡ Charging strike...", 
    "🎯 Locking on...", 
    "🚀 Swing! 0.5s to impact...", 
    "💥 KABOOM! 💥", 
    "💀 USER PERMANENTLY BANNED 💀", 
    "❌"
]
mute_ani = [
    "🤫 Initiating Silence protocol...", 
    "🤐 Sealing the lips...", 
    "🔒 Applying magic lock...", 
    "🗝️ Key turned!", 
    "🤫 Shhh... no more noise.", 
    "🤐 MUTED! 🤐", 
    "✅"
]
unmute_ani = [
    "🔓 Breaking the seal...", 
    "🗝️ Unlocking the mouth...", 
    "🍃 Restoring voice...", 
    "🔥 Vibe check... Passed!", 
    "🗣️ You are free to speak!", 
    "✅"
]


# ── Helpers ───────────────────────────────────────────────────────────────────

async def send_gif_with_caption(client: Client, chat_id: int, gif_key: str, caption: str):
    """Attempt to send a GIF with a caption."""
    url = await get_random_gif(gif_key)
    if not url:
        return None
    
    try:
        # Try sending by URL first
        return await client.send_animation(chat_id, url, caption=caption)
    except Exception as e:
        # Fallback: Download and send
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=20) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        temp_name = f"temp_{gif_key}_{random.randint(100,999)}.gif"
                        with open(temp_name, "wb") as f:
                            f.write(data)
                        
                        sent = await client.send_animation(chat_id, temp_name, caption=caption)
                        os.remove(temp_name)
                        return sent
                    else:
                        LOGGER.warning(f"GIF Download failed for {gif_key} ({url}): Status {resp.status}")
        except Exception as e2:
            LOGGER.warning(f"GIF Fallback failed for {gif_key} ({url}): {e2}")
    return None


async def animate(client: Client, message: Message, gif_key: str, frames: list, action_verb: str, sleep: float = 0.5):
    """Perform text animation, then send GIF with caption."""
    if not message.reply_to_message:
        await message.reply_text(f"❗ Please reply to a user to {gif_key} them!")
        return

    sender = message.from_user.mention
    target = message.reply_to_message.from_user.mention
    caption = f"✨ {sender} {action_verb} {target}! ✨"

    # Start text animation
    msg = await message.reply_text(frames[0])
    
    # Avoid FloodWait: Limit to ~8 edits if the list is long
    total_frames = len(frames)
    step = 1
    if total_frames > 8:
        step = total_frames // 7
        if step == 0: step = 1

    for x in range(step, total_frames, step):
        try:
            await msg.edit_text(frames[x])
            await asyncio.sleep(sleep)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except RPCError:
            break
    
    # Send the GIF with caption
    gif_msg = await send_gif_with_caption(client, message.chat.id, gif_key, caption)
    
    # Only delete the temporary text animation message if GIF succeeded
    # Otherwise, edit it to keep the result visible
    if gif_msg:
        try:
            await msg.delete()
        except:
            pass
    else:
        try:
            await msg.edit_text(caption)
        except:
            pass

async def admin_animate(client: Client, message: Message, gif_key: str, frames: list, action_verb: str, admin_func, reason: str = None):
    """Integrated animation for Admin commands (ban/mute)."""
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text(f"❗ Please reply to a user or provide a username to {gif_key} them!")
        return

    # Check target
    from QueenNoxi.modules.helper_funcs.extraction import extract_user_and_text
    user_id, extracted_reason = await extract_user_and_text(message, message.command[1:])
    
    # Use provided reason or extracted one
    final_reason = reason or extracted_reason
    
    if not user_id:
        await message.reply_text("ɪ ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ.")
        return

    try:
        member = await message.chat.get_member(user_id)
    except:
        await message.reply_text("ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴘᴇʀsᴏɴ.")
        return

    # Check for admin protection
    from QueenNoxi.modules.helper_funcs.chat_status import is_user_ban_protected
    if gif_key in ["ban", "mute"] and await is_user_ban_protected(message.chat, user_id, member):
        await message.reply_text("✨ ᴛʜɪs ᴜsᴇʀ sᴇᴇᴍs ᴛᴏ ʙᴇ ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʙʏ ᴀ ᴍɪɢʜᴛʏ ʙᴀʀʀɪᴇʀ! ɪ ᴄᴀɴɴᴏᴛ ʜᴀʀᴍ ᴀ ғᴇʟʟᴏᴡ ᴀᴅᴍɪɴ. ✨")
        return

    # Try the admin action first
    try:
        success = await admin_func(user_id)
        if not success:
            return
    except Exception as e:
        await message.reply_text(f"❌ Administration failed: {e}")
        return

    sender_mention = message.from_user.mention
    target_mention = member.user.mention
    
    # Matching the regular ban/mute format
    title = "ʙᴀɴ ᴇᴠᴇɴᴛ" if gif_key == "ban" else "ᴍᴜᴛᴇ ᴇᴠᴇɴᴛ"
    emoji = "❕" if gif_key == "ban" else "🕵️"
    
    caption = (
        f"<code>{emoji}</code><b>{title}</b>\n"
        f"<code> </code><b>•  {'ʙᴀɴɴᴇᴅ' if gif_key == 'ban' else 'ᴍᴜᴛᴇᴅ'} ʙʏ:</b> {sender_mention}\n"
        f"<code> </code><b>•  ᴜsᴇʀ:</b> {target_mention}"
    )
    if final_reason:
        caption += f"\n<code> </code><b>•  ʀᴇᴀsᴏɴ:</b> \n{html.escape(final_reason)}"

    # Text animation
    msg = await message.reply_text(frames[0])
    total_frames = len(frames)
    for x in range(1, total_frames):
        try:
            await msg.edit_text(frames[x])
            await asyncio.sleep(0.5)
        except:
            break
            
    # GIF result
    gif_msg = await send_gif_with_caption(client, message.chat.id, gif_key, caption)
    if gif_msg:
        try:
            await msg.delete()
        except:
            pass
    else:
        try:
            await msg.edit_text(caption)
        except:
            pass




# ── Commands ──────────────────────────────────────────────────────────────────
@pbot.on_message(filters.command("dlanimech"))
async def dlanimech(client: Client, message: Message):
    """Zip and send animation cache to Sudoers in PM."""
    if message.from_user.id not in SUDOERS:
        await message.reply_text("❌ This command is only for Sudoers/Owners!")
        return

    msg = await message.reply_text("📦 Zipping animation cache...")
    
    zip_path = "anim_cache.zip"
    try:
        # Create zip
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(CACHE_DIR):
                for file in files:
                    zipf.write(
                        os.path.join(root, file),
                        os.path.relpath(os.path.join(root, file), os.path.join(CACHE_DIR, '..'))
                    )
        
        # Send in PM
        await client.send_document(
            chat_id=message.from_user.id,
            document=zip_path,
            caption="📂 Here is the current Animation Cache!",
            file_name="animation_cache.zip"
        )
        await msg.edit_text("✅ Sent to your PM!")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

@pbot.on_message(filters.command("brain") & filters.group)
@DisableAbleCommandHandler("brain")
async def brainanimation(client: Client, message: Message):
    await animate(client, message, "brain", brain_chain, "put brain in dustbin for")

@pbot.on_message(filters.command("clock") & filters.group)
@DisableAbleCommandHandler("clock")
async def clockanimation(client: Client, message: Message):
    await animate(client, message, "clock", clock_ani, "reminded time to")

@pbot.on_message(filters.command("police") & filters.group)
@DisableAbleCommandHandler("police")
async def policeanimation(client: Client, message: Message):
    await animate(client, message, "police", police_ani, "called police for")

@pbot.on_message(filters.command("moon") & filters.group)
@DisableAbleCommandHandler("moon")
async def moonanimation(client: Client, message: Message):
    await animate(client, message, "moon", moon_ani, "wished good night to")

@pbot.on_message(filters.command("bombs") & filters.group)
@DisableAbleCommandHandler("bombs")
async def bombs(client: Client, message: Message):
    await animate(client, message, "bombs", bomb_ettu, "bombed")

@pbot.on_message(filters.command("hack") & filters.group)
@DisableAbleCommandHandler("hack")
async def hack(client: Client, message: Message):
    await animate(client, message, "hack", hack_you, "hacked")

@pbot.on_message(filters.command("love") & filters.group)
@DisableAbleCommandHandler("love")
async def love(client: Client, message: Message):
    await animate(client, message, "love", love_siren, "is expressing love to")

@pbot.on_message(filters.command("kill") & filters.group)
@DisableAbleCommandHandler("kill")
async def kill(client: Client, message: Message):
    await animate(client, message, "kill", kill_you, "killed")

@pbot.on_message(filters.command("slap") & filters.group)
@DisableAbleCommandHandler("slap")
async def slap(client: Client, message: Message):
    await animate(client, message, "slap", slap_ani, "slapped")

@pbot.on_message(filters.command("pat") & filters.group)
@DisableAbleCommandHandler("pat")
async def pat(client: Client, message: Message):
    await animate(client, message, "pat", pat_ani, "patted")

@pbot.on_message(filters.command("hug") & filters.group)
@DisableAbleCommandHandler("hug")
async def hug(client: Client, message: Message):
    await animate(client, message, "hug", hug_ani, "hugged")

@pbot.on_message(filters.command("kiss") & filters.group)
@DisableAbleCommandHandler("kiss")
async def kiss(client: Client, message: Message):
    await animate(client, message, "kiss", kiss_ani, "kissed")

@pbot.on_message(filters.command("aban") & filters.group)
@user_admin
@bot_admin
@user_can_ban
@can_restrict
async def aban_cmd(client: Client, message: Message):
    async def ban_logic(uid):
        try:
            await message.chat.ban_member(uid)
            return True
        except RPCError as e:
            await message.reply_text(f"❌ Failed to ban: {e.MESSAGE}")
            return False
            
    await admin_animate(client, message, "ban", ban_ani, "banned", ban_logic)

@pbot.on_message(filters.command("amute") & filters.group)
@user_admin
@bot_admin
@can_restrict
async def amute_cmd(client: Client, message: Message):
    async def mute_logic(uid):
        from pyrogram.types import ChatPermissions
        try:
            await message.chat.restrict_member(uid, ChatPermissions(can_send_messages=False))
            return True
        except RPCError as e:
            await message.reply_text(f"❌ Failed to mute: {e.MESSAGE}")
            return False
            
    await admin_animate(client, message, "mute", mute_ani, "muted", mute_logic)

@pbot.on_message(filters.command("aunmute") & filters.group)
@user_admin
@bot_admin
@can_restrict
async def aunmute_cmd(client: Client, message: Message):
    async def unmute_logic(uid):
        from pyrogram.types import ChatPermissions
        try:
            await message.chat.restrict_member(
                uid,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True
                )
            )
            return True
        except RPCError as e:
            await message.reply_text(f"❌ Failed to unmute: {e.MESSAGE}")
            return False
            
    await admin_animate(client, message, "unmute", unmute_ani, "unmuted", unmute_logic)



__mod_name__ = "Animation"
__help__ = """
*ғᴀᴋᴇ ᴀɴɪᴍᴀᴛɪᴏɴ ᴄᴏᴍᴍᴀɴᴅs*
• `/love` — ʟᴏᴠᴇ ᴀɴɪᴍᴀᴛɪᴏɴ
• `/hack` — ʜᴀᴄᴋ ᴀɴɪᴍᴀᴛɪᴏɴ
• `/moon` — ᴍᴏᴏɴ ᴀɴɪᴍᴀᴛɪᴏɴ
• `/kill` — ᴋɪʟʟ ᴀɴɪᴍᴀᴛɪᴏɴ
• `/slap` — sʟᴀᴩ ᴀɴɪᴍᴀᴛɪᴏɴ
• `/pat` — ᴩᴀᴛ ᴀɴɪᴍᴀᴛɪᴏɴ
• `/hug` — ʜᴜɢ ᴀɴɪᴍᴀᴛɪᴏɴ
• `/kiss` — ᴋɪss ᴀɴɪᴍᴀᴛɪᴏɴ
• `/bombs` — ʙᴏᴍʙ ᴀɴɪᴍᴀᴛɪᴏɴ
• `/police` — ᴩᴏʟɪᴄᴇ ᴀɴɪᴍᴀᴛɪᴏɴ
• `/brain` — ʙʀᴀɪɴ ᴀɴɪᴍᴀᴛɪᴏɴ
• `/clock` — ᴄʟᴏᴄᴋ ᴀɴɪᴍᴀᴛɪᴏɴ
• `/aban` — ᴀɴɪᴍᴀᴛᴇᴅ ʙᴀɴ
• `/amute` — ᴀɴɪᴍᴀᴛᴇᴅ ᴍᴜᴛᴇ
• `/aunmute` — ᴀɴɪᴍᴀᴛᴇᴅ ᴜɴᴍᴜᴛᴇ
"""

