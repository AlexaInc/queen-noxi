import html
from pyrogram import filters, Client, enums
from pyrogram.types import Message

from QueenNoxi import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    OWNER_ID,
    TIGERS,
    WOLVES,
    pbot,
)
from QueenNoxi.modules.helper_funcs.chat_status import (
    dev_plus,
    sudo_plus,
    whitelist_plus,
)
from QueenNoxi.modules.helper_funcs.extraction import extract_user
from QueenNoxi.modules.log_channel import gloggable

async def check_user_id(user_id: int, client: Client) -> str:
    if not user_id:
        return "That...is a chat! baka ka omae?"
    if user_id == (await client.get_me()).id:
        return "This does not work that way."
    return None

@pbot.on_message(filters.command("addsudo") & filters.user(OWNER_ID))
@dev_plus
@gloggable
async def addsudo(client: Client, message: Message) -> str:
    user_id = await extract_user(message, message.command[1:])
    reply = await check_user_id(user_id, client)
    if reply:
        await message.reply_text(reply)
        return ""

    if user_id in DRAGONS:
        await message.reply_text("This member is already a Dragon Disaster")
        return ""

    if user_id in DEMONS: DEMONS.remove(user_id)
    if user_id in WOLVES: WOLVES.remove(user_id)
    if user_id in TIGERS: TIGERS.remove(user_id)

    DRAGONS.append(user_id)
    user_member = await client.get_users(user_id)
    await message.reply_text(f"Successfully set Disaster level of {user_member.first_name} to Dragon!")

    return f"#SUDO\n**Admin:** {message.from_user.mention}\n**User:** {user_member.mention}"

@pbot.on_message(filters.command(["addsupport", "adddemon"]) & filters.user(DRAGONS))
@sudo_plus
@gloggable
async def addsupport(client: Client, message: Message) -> str:
    user_id = await extract_user(message, message.command[1:])
    reply = await check_user_id(user_id, client)
    if reply:
        await message.reply_text(reply)
        return ""

    if user_id in DEMONS:
        await message.reply_text("This user is already a Demon Disaster.")
        return ""

    if user_id in DRAGONS: DRAGONS.remove(user_id)
    if user_id in WOLVES: WOLVES.remove(user_id)
    if user_id in TIGERS: TIGERS.remove(user_id)

    DEMONS.append(user_id)
    user_member = await client.get_users(user_id)
    await message.reply_text(f"{user_member.first_name} was added as a Demon Disaster!")

    return f"#SUPPORT\n**Admin:** {message.from_user.mention}\n**User:** {user_member.mention}"

@pbot.on_message(filters.command(["addwhitelist", "addwolf"]) & filters.user(DRAGONS))
@sudo_plus
@gloggable
async def addwhitelist(client: Client, message: Message) -> str:
    user_id = await extract_user(message, message.command[1:])
    reply = await check_user_id(user_id, client)
    if reply:
        await message.reply_text(reply)
        return ""

    if user_id in WOLVES:
        await message.reply_text("This user is already a Wolf Disaster.")
        return ""

    for l in [DRAGONS, DEMONS, TIGERS]:
        if user_id in l: l.remove(user_id)

    WOLVES.append(user_id)
    user_member = await client.get_users(user_id)
    await message.reply_text(f"Successfully promoted {user_member.first_name} to a Wolf Disaster!")

    return f"#WHITELIST\n**Admin:** {message.from_user.mention}\n**User:** {user_member.mention}"

@pbot.on_message(filters.command("addtiger") & filters.user(DRAGONS))
@sudo_plus
@gloggable
async def addtiger(client: Client, message: Message) -> str:
    user_id = await extract_user(message, message.command[1:])
    reply = await check_user_id(user_id, client)
    if reply:
        await message.reply_text(reply)
        return ""

    if user_id in TIGERS:
        await message.reply_text("This user is already a Tiger.")
        return ""

    for l in [DRAGONS, DEMONS, WOLVES]:
        if user_id in l: l.remove(user_id)

    TIGERS.append(user_id)
    user_member = await client.get_users(user_id)
    await message.reply_text(f"Successfully promoted {user_member.first_name} to a Tiger Disaster!")

    return f"#TIGER\n**Admin:** {message.from_user.mention}\n**User:** {user_member.mention}"

@pbot.on_message(filters.command(["removesudo", "rmsudo"]) & filters.user(OWNER_ID))
@dev_plus
@gloggable
async def removesudo(client: Client, message: Message) -> str:
    user_id = await extract_user(message, message.command[1:])
    if user_id in DRAGONS:
        DRAGONS.remove(user_id)
        user_member = await client.get_users(user_id)
        await message.reply_text("Demoted user to Civilian.")
        return f"#UNSUDO\n**Admin:** {message.from_user.mention}\n**User:** {user_member.mention}"
    await message.reply_text("This user is not a Dragon Disaster!")
    return ""

@pbot.on_message(filters.command(["removesupport", "removedemon"]) & filters.user(DRAGONS))
@sudo_plus
@gloggable
async def removesupport(client: Client, message: Message) -> str:
    user_id = await extract_user(message, message.command[1:])
    if user_id in DEMONS:
        DEMONS.remove(user_id)
        user_member = await client.get_users(user_id)
        await message.reply_text("Demoted user to Civilian.")
        return f"#UNSUPPORT\n**Admin:** {message.from_user.mention}\n**User:** {user_member.mention}"
    await message.reply_text("This user is not a Demon level Disaster!")
    return ""

@pbot.on_message(filters.command(["sudolist", "dragons"]))
@whitelist_plus
async def sudolist(client: Client, message: Message):
    true_sudo = list(set(DRAGONS) - set(DEV_USERS))
    reply = "**Known Dragon Disasters 🐉:**\n"
    for each_user in true_sudo:
        try:
            user = await client.get_users(each_user)
            reply += f"• {user.mention}\n"
        except: pass
    await message.reply_text(reply)

@pbot.on_message(filters.command(["supportlist", "demons"]))
@whitelist_plus
async def supportlist(client: Client, message: Message):
    reply = "**Known Demon Disasters 👹:**\n"
    for each_user in DEMONS:
        try:
            user = await client.get_users(each_user)
            reply += f"• {user.mention}\n"
        except: pass
    await message.reply_text(reply)

@pbot.on_message(filters.command(["wolves", "whitelistlist"]))
@whitelist_plus
async def wolveslist(client: Client, message: Message):
    reply = "**Known Wolf Disasters 🐺:**\n"
    for each_user in WOLVES:
        try:
            user = await client.get_users(each_user)
            reply += f"• {user.mention}\n"
        except: pass
    await message.reply_text(reply)

@pbot.on_message(filters.command("tigers"))
@whitelist_plus
async def tigerslist(client: Client, message: Message):
    reply = "**Known Tiger Disasters 🐯:**\n"
    for each_user in TIGERS:
        try:
            user = await client.get_users(each_user)
            reply += f"• {user.mention}\n"
        except: pass
    await message.reply_text(reply)

@pbot.on_message(filters.command("devlist"))
@whitelist_plus
async def devlist(client: Client, message: Message):
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply = "✨ **Devs User List:**\n"
    for each_user in true_dev:
        try:
            user = await client.get_users(each_user)
            reply += f"• {user.mention}\n"
        except: pass
    await message.reply_text(reply)

__mod_name__ = "Dᴇᴠꜱ"
__help__ = """
★ /sudolist: lists all dragons
★ /supportlist: lists all demons
★ /wolves: lists all wolves
★ /tigers: lists all tigers
★ /devlist: lists hero association members
"""
