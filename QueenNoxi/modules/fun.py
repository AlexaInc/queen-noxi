import html
import random
import requests
import asyncio
from pyrogram import filters, Client, enums
from pyrogram.types import Message

import QueenNoxi.modules.fun_strings as fun_strings
from QueenNoxi import pbot, OWNER_ID
from QueenNoxi.modules.helper_funcs.extraction import extract_user

@pbot.on_message(filters.command("runs"))
async def runs(client: Client, message: Message):
    await message.reply_text(random.choice(fun_strings.RUN_STRINGS))

@pbot.on_message(filters.command("slap"))
async def slap(client: Client, message: Message):
    user_id = await extract_user(message, message.command[1:])
    curr_user = message.from_user.first_name
    
    if not user_id:
        user1 = (await client.get_me()).first_name
        user2 = curr_user
    else:
        user = await client.get_users(user_id)
        user1 = curr_user
        user2 = user.first_name

    temp = random.choice(fun_strings.SLAP_TEMPLATES)
    item = random.choice(fun_strings.ITEMS)
    hit = random.choice(fun_strings.HIT)
    throw = random.choice(fun_strings.THROW)
    
    reply = temp.format(user1=html.escape(user1), user2=html.escape(user2), item=item, hits=hit, throws=throw)
    await message.reply_text(reply)

@pbot.on_message(filters.command("pat"))
async def pat(client: Client, message: Message):
    user_id = await extract_user(message, message.command[1:])
    curr_user = message.from_user.first_name
    
    if not user_id:
        user1 = (await client.get_me()).first_name
        user2 = curr_user
    else:
        user = await client.get_users(user_id)
        user1 = curr_user
        user2 = user.first_name

    temp = random.choice(fun_strings.PAT_TEMPLATES)
    reply = temp.format(user1=html.escape(user1), user2=html.escape(user2))
    await message.reply_text(reply)

@pbot.on_message(filters.command("roll"))
async def roll(client: Client, message: Message):
    await message.reply_text(str(random.randint(1, 6)))

@pbot.on_message(filters.command("toss"))
async def toss(client: Client, message: Message):
    await message.reply_text(random.choice(fun_strings.TOSS))

@pbot.on_message(filters.command("shrug"))
async def shrug(client: Client, message: Message):
    await message.reply_text(r"¯\_(ツ)_/¯")

@pbot.on_message(filters.command("decide"))
async def decide(client: Client, message: Message):
    await message.reply_text(random.choice(fun_strings.DECIDE))

@pbot.on_message(filters.command("8ball"))
async def eightball(client: Client, message: Message):
    await message.reply_text(random.choice(fun_strings.EIGHTBALL))

@pbot.on_message(filters.command("kiss"))
async def kiss(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("You need to reply to a user's message to kiss them!")
        return

    sender = message.from_user
    replied_user = message.reply_to_message.from_user

    if not replied_user:
        await message.reply_text("You need to reply to a valid user to kiss them!")
        return

    if sender.id == replied_user.id:
        await message.reply_text("You can't kiss yourself, that's sad!")
        return

    try:
        req = requests.get("https://nekos.life/api/v2/img/kiss", timeout=5).json()
        gif_url = req.get("url")
    except Exception:
        gif_url = "https://cdn.nekos.life/kiss/kiss_001.gif"

    caption = f"[{sender.first_name}](tg://user?id={sender.id}) gives a sweet kiss to [{replied_user.first_name}](tg://user?id={replied_user.id}) 💋"

    await message.reply_animation(
        animation=gif_url,
        caption=caption,
        reply_to_message_id=message.id
    )

__mod_name__ = "Fun"
__help__ = """
• `/runs`: Random strings!
• `/slap`: Slap someone!
• `/pat`: Pat someone!
• `/roll`: Roll a dice!
• `/toss`: Toss a coin!
• `/shrug`: Shrug!
• `/decide`: Yes/No/Maybe?
• `/8ball`: Ask the 8-ball!
• `/kiss`: Give someone a sweet kiss!
"""
