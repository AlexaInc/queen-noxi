import importlib
import re
import time
import asyncio
from platform import python_version as y
from sys import argv, exit as sys_exit

from pyrogram import filters, enums, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram import __version__ as pyrover
from pyrogram.errors import FloodWait, RPCError, AuthKeyDuplicated, Unauthorized

from telethon import __version__ as tlhver
from telethon.errors import FloodWaitError as TlFloodWait

from QueenNoxi import (
    BOT_ID,
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    OWNER_ID,
    START_IMG,
    SUPPORT_CHAT,
    SUPPORT_CHAT_URL,
    TOKEN,
    StartTime,
    pbot,
    telethn,
    aiohttpsession
)
from QueenNoxi.modules import ALL_MODULES
from QueenNoxi.modules.no_sql.users_db import get_served_users
from QueenNoxi.modules.no_sql.chats_db import get_served_chats
from QueenNoxi.modules.helper_funcs.misc import paginate_modules
from QueenNoxi.modules.sql.session_sql import save_session, delete_session

# SUPPORT_CHAT_URL is now centralized in QueenNoxi.__init__

# --- DEBUG COMMAND LOGGER ---
@pbot.on_message(filters.group & filters.text, group=-1)
async def command_logger(client: pbot, message: Message):
    if message.text and (message.text.startswith("/") or message.text.startswith("!")):
        chat_title = message.chat.title if message.chat else "Private"
        user_id = message.from_user.id if message.from_user else (message.sender_chat.id if message.sender_chat else "Unknown")
        LOGGER.info(f"[COMMAND] Chat: {chat_title} ({message.chat.id}) | User: {user_id} | Text: {message.text}")

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time

PM_START_TEX = """
ʜᴇʟʟᴏ `{}`, ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ 
ᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ ʙʀᴏ . . . 
"""

PM_START_TEXT = """ 
*ʜᴇʏ* {} , 🥀
*๏ ɪ'ᴍ {} ʜᴇʀᴇ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘs!
ʜɪᴛ ʜᴇʟᴘ ᴛᴏ ғɪɴᴅ ᴏᴜᴛ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ ɪɴ ᴍʏ ғᴜʟʟ ᴘᴏᴛᴇɴᴛɪᴀʟ!*
➻ *ᴛʜᴇ ᴍᴏsᴛ ᴩᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴩ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ᴀɴᴅ ɪ ʜᴀᴠᴇ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ᴀɴᴅ ᴜsᴇғᴜʟ ғᴇᴀᴛᴜʀᴇs.*
"""

buttons = [
    [
        InlineKeyboardButton(text="🛡️", callback_data="queennoxi_"),
        InlineKeyboardButton(text="💳", callback_data="source_"),
        InlineKeyboardButton(text="🧑‍💻", callback_data="owner_main"),
        InlineKeyboardButton(text="🖥️", callback_data="Main_help"),
     ],
    [
        InlineKeyboardButton(
            text="Aᴅᴅ Mᴇ ᴛᴏ Yᴏᴜʀ Gʀᴏᴜᴘ",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(text="📚 ʜᴇʟᴘ ᴀɴᴅ ᴄᴏᴍᴍᴀᴀɴᴅs", callback_data="Main_help"),
    ],
]

HELP_STRINGS = f"""
» *{BOT_NAME}  ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟʟᴏᴡ ᴛᴏ ɢᴇᴛ ᴅᴇsᴄʀɪᴘᴛɪᴏᴘ ᴀʙᴏᴜᴛ sᴘᴇᴄɪғɪᴄs ᴄᴏᴍᴍᴀɴᴅ*"""

IMPORTED = {}
HELPABLE = {}
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    try:
        imported_module = importlib.import_module("QueenNoxi.modules." + module_name)
        if not hasattr(imported_module, "__mod_name__"):
            imported_module.__mod_name__ = imported_module.__name__
        
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
        if hasattr(imported_module, "__help__") and imported_module.__help__:
            HELPABLE[imported_module.__mod_name__.lower()] = imported_module
            
        if hasattr(imported_module, "__chat_settings__"):
            CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

        if hasattr(imported_module, "__user_settings__"):
            USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module
            
    except Exception as e:
        LOGGER.error(f"Error loading module {module_name}: {e}")

async def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    await pbot.send_photo(
        chat_id=chat_id,
        photo=START_IMG,
        caption=text,
        reply_markup=keyboard,
    )

@pbot.on_message(filters.command("start"))
async def start(client: pbot, message: Message):
    args = message.command[1:]
    uptime = get_readable_time((time.time() - StartTime))
    if message.chat.type == enums.ChatType.PRIVATE:
        if len(args) >= 1:
            if args[0].lower() == "help":
                await send_help(message.chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                await send_help(
                    message.chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="◁", callback_data="help_back")]]
                    ),
                )
        else:
            first_name = message.from_user.first_name if message.from_user else "User"
            # Animation effect
            lol = await message.reply_text(PM_START_TEX.format(first_name))
            await asyncio.sleep(0.3)
            await lol.edit_text("❤")
            await asyncio.sleep(0.2)
            await lol.edit_text("ꜱᴛᴀʀᴛɪɴɢ... ")
            await asyncio.sleep(0.2)
            await lol.delete()
            
            await message.reply_photo(
                START_IMG,
                caption=PM_START_TEXT.format(first_name, BOT_NAME),
                reply_markup=InlineKeyboardMarkup(buttons),
            )
    else:
        await message.reply_photo(
            START_IMG,
            caption="ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ  !\n<b>ɪ ᴅɪᴅɴ'ᴛ sʟᴇᴘᴛ sɪɴᴄᴇ​:</b> <code>{}</code>".format(uptime),
            parse_mode=enums.ParseMode.HTML,
        )

@pbot.on_callback_query(filters.regex(r"^help_"))
async def help_button(client, query: CallbackQuery):
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "» *ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs ꜰᴏʀ​​* *{}* :\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            try:
                await query.message.edit_caption(text,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="help_back"),
                          InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", callback_data="queennoxi_support")]]
                    ),
                )
            except RPCError as e:
                # Fallback if caption is still too long or other RPC error
                LOGGER.error(f"Error editing help caption: {e}")
                await query.message.reply_text(text,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="help_back"),
                          InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", callback_data="queennoxi_support")]]
                    ),
                )
        elif prev_match:
            curr_page = int(prev_match.group(1))
            await query.message.edit_caption(HELP_STRINGS,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )
        elif next_match:
            next_page = int(next_match.group(1))
            await query.message.edit_caption(HELP_STRINGS,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )
        elif back_match:
            await query.message.edit_caption(HELP_STRINGS,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )
        await query.answer()
    except Exception as e:
        LOGGER.error(f"Error in help_button: {e}")
        await query.answer("An error occurred while opening help.", show_alert=True)

@pbot.on_callback_query(filters.regex(r"^queennoxi_"))
async def QueenNoxi_about_callback(client, query: CallbackQuery):
    if query.data == "queennoxi_":
        uptime = get_readable_time((time.time() - StartTime))
        users = await get_served_users()
        chats = await get_served_chats()
        await query.message.edit_caption(
            f"*ʜᴇʏ,*🥀\n  *ᴛʜɪs ɪs {BOT_NAME}*"
            "\n*ᴀ ᴘᴏᴡᴇʀꜰᴜʟ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ➕ ᴍᴜsɪᴄ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴜɪʟᴛ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴇᴀꜱɪʟʏ ᴀɴᴅ ᴛᴏ ᴘʀᴏᴛᴇᴄᴛ ʏᴏᴜʀ ɢʀᴏᴜᴘ ꜰʀᴏᴍ ꜱᴄᴀᴍᴍᴇʀꜱ ᴀɴᴅ ꜱᴘᴀᴍᴍᴇʀꜱ.*"
            "\n*ᴡʀɪᴛᴛᴇɴ ɪɴ ᴩʏᴛʜᴏɴ ᴡɪᴛʜ sǫʟᴀʟᴄʜᴇᴍʏ ᴀɴᴅ ᴍᴏɴɢᴏᴅʙ ᴀs ᴅᴀᴛᴀʙᴀsᴇ.*"
            "\n\n────────────────────"
            f"\n*➻ ᴜᴩᴛɪᴍᴇ »* {uptime}"
            f"\n* ᴜꜱᴇʀꜱ : {len(users)} "
            f"\n* ᴄʜᴀᴛs : {len(chats)} "
            "\n────────────────────"
            "\n➲  ɪ ᴄᴀɴ ʀᴇꜱᴛʀɪᴄᴛ ᴜꜱᴇʀꜱ."
            "\n➲  ɪ ʜᴀᴠᴇ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴛɪ-ꜰʟᴏᴏᴅ ꜱʏꜱᴛᴇᴍ."
            "\n➲  ɪ ᴄᴀɴ ɢʀᴇᴇᴛ ᴜꜱᴇʀꜱ ᴡɪᴛʜ ᴄᴜꜱᴛᴏᴍɪᴢᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ᴀɴᴅ ᴇᴠᴇɴ ꜱᴇᴛ ᴀ ɢʀᴏᴜᴘ'ꜱ ʀᴜʟᴇꜱ."
            f"\n\n➻ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ғᴏʀ ɢᴇᴛᴛɪɴɢ ʙᴀsɪᴄ ʜᴇʟᴩ ᴀɴᴅ ɪɴғᴏ ᴀʙᴏᴜᴛ {BOT_NAME}.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="🏡", callback_data="queennoxi_back"),
                        InlineKeyboardButton(text="💳", callback_data="source_"),
                        InlineKeyboardButton(text="🧑‍💻", url=f"tg://user?id={OWNER_ID}"),
                        InlineKeyboardButton(text="🖥️", callback_data="Main_help"),
                    ],
                    [
                        InlineKeyboardButton(text="🚩sᴜᴩᴩᴏʀᴛ", callback_data="queennoxi_support"),
                        InlineKeyboardButton(text="ᴄᴏᴍᴍᴀɴᴅs 💁", callback_data="Main_help"),
                    ],
                    [
                        InlineKeyboardButton(text="👨‍💻ᴅᴇᴠᴇʟᴏᴩᴇʀ", url=f"tg://user?id={OWNER_ID}"),
                    ],
                ]
            ),
        )
    elif query.data == "queennoxi_back":
        await query.message.edit_caption(
            PM_START_TEXT.format(query.from_user.first_name if query.from_user else "User", BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    elif query.data == "queennoxi_support":
        await query.message.edit_caption(
            "ʜᴇʏ 👋\nᴄʟɪᴄᴋ sᴜᴩᴩᴏʀᴛ ᴛᴏ ᴊᴏɪɴ sᴜᴩᴩᴏʀᴛ ɢʀᴏᴜᴩ.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("sᴜᴩᴩᴏʀᴛ", url=SUPPORT_CHAT_URL)],
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="queennoxi_back")]
            ])
        )
    await query.answer()

@pbot.on_callback_query(filters.regex(r"^Main_help"))
async def Main_help_callback(client, query: CallbackQuery):
    await query.message.edit_caption(
        HELP_STRINGS,
        reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    )
    await query.answer()

@pbot.on_callback_query(filters.regex(r"^source_"))
async def Source_about_callback(client, query: CallbackQuery):
    if query.data == "source_":
        await query.message.edit_caption(
            f"*ʜᴇʏ,\n ᴛʜɪs ɪs {BOT_NAME}*\n\n"
            "*ʜᴇʀᴇ ɪs ᴍʏ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ :* [ɢɪᴛʜᴜʙ](https://github.com/AlexaInc/queen-noxi)",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text="sᴏᴜʀᴄᴇ", url="https://github.com/AlexaInc/queen-noxi")],
                    [
                        InlineKeyboardButton(text="🏡", callback_data="queennoxi_back"),
                        InlineKeyboardButton(text="🛡️", callback_data="queennoxi_"),
                        InlineKeyboardButton(text="💳", callback_data="source_"),
                        InlineKeyboardButton(text="🖥️", callback_data="Main_help"),
                    ],
                    [InlineKeyboardButton(text="◁", callback_data="source_back")]
                ]
            ),
        )
    elif query.data == "source_back":
        await query.message.edit_caption(
            PM_START_TEXT.format(query.from_user.first_name if query.from_user else "User", BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    await query.answer()

@pbot.on_callback_query(filters.regex(r"^owner_"))
async def owner_callback(client, query: CallbackQuery):
    data = query.data
    if data == "owner_main":
        from QueenNoxi import OWNER_IDS
        owner_buttons = []
        for oid in OWNER_IDS:
            try:
                user = await client.get_users(oid)
                name = user.first_name
                # Use username if available for better redirection
                if user.username:
                    url = f"https://t.me/{user.username}"
                else:
                    # Fallback to tg://user?id= which works in most modern clients if used correctly
                    url = f"tg://user?id={oid}"
                owner_buttons.append([InlineKeyboardButton(text=f"👤 {name}", url=url)])
            except Exception:
                owner_buttons.append([InlineKeyboardButton(text=f"👤 Owner {oid}", url=f"tg://user?id={oid}")])
        
        if not owner_buttons:
            owner_buttons.append([InlineKeyboardButton(text="👤 Main Owner", url=f"tg://user?id={OWNER_ID}")])

        owner_buttons.append([InlineKeyboardButton(text="◁ Back", callback_data="queennoxi_back")])
        
        await query.message.edit_caption(
            "✨ **Owner Selection Menu**\n\nChoose an owner profile to view:",
            reply_markup=InlineKeyboardMarkup(owner_buttons),
        )
    await query.answer()


@pbot.on_callback_query(filters.regex(r"^Music_"))
async def music_callback(client, query: CallbackQuery):
    data = query.data
    NAV = [
        InlineKeyboardButton("🏡", callback_data="queennoxi_back"),
        InlineKeyboardButton("🛡️", callback_data="queennoxi_"),
        InlineKeyboardButton("💳", callback_data="source_"),
        InlineKeyboardButton("🖥️", callback_data="Main_help"),
    ]
    if data == "Music_":
        await query.message.edit_caption(
            "ʜᴇʀᴇ ɪꜱ ʜᴇʟᴘ ᴍᴇɴᴜ ꜰᴏʀ ᴍᴜꜱɪᴄ",
            reply_markup=InlineKeyboardMarkup([
                NAV,
                [InlineKeyboardButton("⍟ ᴀᴅᴍɪɴ ⍟", callback_data="Music_admin"),
                 InlineKeyboardButton("⍟ ᴘʟᴀʏ ⍟", callback_data="Music_play")],
                [InlineKeyboardButton("⍟ ʙᴏᴛ ⍟", callback_data="Music_bot"),
                 InlineKeyboardButton("⍟ ᴇxᴛʀᴀ ⍟", callback_data="Music_extra")],
                [InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="Main_help")],
            ]),
        )
    elif data == "Music_admin":
        await query.message.edit_caption(
            "*» ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ «*\n"
            "/pause – ᴩᴀᴜsᴇ stream\n/resume – ʀᴇsᴜᴍᴇ\n"
            "/skip – sᴋɪᴩ ᴄᴜʀʀᴇɴᴛ\n/end,/stop – sᴛᴏᴩ & ᴄʟᴇᴀʀ ǫᴜᴇᴜᴇ\n"
            "/player – ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴩᴀɴᴇʟ\n/queue – sʜᴏᴡ ǫᴜᴇᴜᴇ",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="Music_"),
                InlineKeyboardButton("sᴜᴩᴩᴏʀᴛ", url=SUPPORT_CHAT_URL),
            ]]),
        )
    elif data == "Music_play":
        await query.message.edit_caption(
            "*» ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅꜱ «*\n"
            "/play, /vplay, /cplay – ᴩʟᴀʏ ᴀᴜᴅɪᴏ/ᴠɪᴅᴇᴏ\n"
            "/playforce – ғᴏʀᴄᴇ ᴩʟᴀʏ\n"
            "/channelplay [id/disable] – ᴄʜᴀɴɴᴇʟ ᴩʟᴀʏ",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="Music_"),
                InlineKeyboardButton("sᴜᴩᴩᴏʀᴛ", url=SUPPORT_CHAT_URL),
            ]]),
        )
    elif data == "Music_bot":
        await query.message.edit_caption(
            "*» ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅꜱ «*\n"
            "/stats – ɢʟᴏʙᴀʟ sᴛᴀᴛs\n/sudolist – sᴜᴅᴏ ᴜsᴇʀs\n"
            "/lyrics [ɴᴀᴍᴇ] – ꜰᴇᴛᴄʜ ʟʏʀɪᴄs\n/song [ɴᴀᴍᴇ/ᴜʀʟ] – ᴅᴏᴡᴀɴʟᴏᴀᴅ",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="Music_"),
                InlineKeyboardButton("sᴜᴩᴩᴏʀᴛ", callback_data="queennoxi_support"),
            ]]),
        )
    elif data == "Music_extra":
        await query.message.edit_caption(
            "*» ᴇxᴛʀᴀ ᴄᴏᴍᴍᴀɴᴅꜱ «*\n"
            "/mstart – sᴛᴀʀᴛ ᴍᴜsɪᴄ ʙᴏᴛ\n/mhelp – ᴍᴜsɪᴄ ʜᴇʟᴩ\n",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("• sᴜᴩᴩᴏʀᴛ •", url=SUPPORT_CHAT_URL)
            ]])
        )
    await query.answer()

async def main():
    import QueenNoxi
    from aiohttp import ClientSession
    QueenNoxi.aiohttpsession = ClientSession()
    
    # --- Pyrogram Start ---
    try:
        await pbot.start()
        LOGGER.info("[Pyrogram] Client started.")
        
        # Export and save session string for persistence
        try:
             ss = await pbot.export_session_string()
             save_session(BOT_ID, ss)
             LOGGER.info("[Pyrogram] Saved session string for persistence.")
        except Exception as e:
             LOGGER.warning(f"Could not export/save session string: {e}")

        await asyncio.sleep(2)
        try:
            if hasattr(pbot, 'delete_webhook'):
                await pbot.delete_webhook(drop_pending_updates=True)
            elif hasattr(pbot, 'delete_web_hook'):
                await pbot.delete_web_hook(drop_pending_updates=True)
            LOGGER.info("[Pyrogram] Webhook cleared and queue flushed.")
        except FloodWait as e:
            LOGGER.warning(f"[Pyrogram] FloodWait while clearing webhook: {e.value}s")
    except FloodWait as e:
        LOGGER.error(f"[Pyrogram] CRITICAL FloodWait on start: {e.value}s. Sleeping...")
        await asyncio.sleep(e.value)
    except (AuthKeyDuplicated, Unauthorized) as e:
        LOGGER.error(f"[Pyrogram] Session invalidated ({e}). Clearing and RESTARTING bot...")
        delete_session(BOT_ID)
        sys_exit(1) # Exit to trigger a container restart

    except Exception as e:
        LOGGER.error(f"[Pyrogram] Failed to start client: {e}")

    # --- Telethon Start ---
    try:
        await telethn.start(bot_token=TOKEN)
        LOGGER.info("[Telethon] Client started.")
        
        # Export and save Telethon session string
        try:
            from telethon.sessions import StringSession
            session_str = telethn.session.save()
            save_session(f"TELETHON_{BOT_ID}", session_str)
            LOGGER.info("[Telethon] Saved session string for persistence.")
        except Exception as e:
            LOGGER.warning(f"Could not export/save Telethon session string: {e}")
            
    except TlFloodWait as e:
        LOGGER.warning(f"[Telethon] FloodWait on start: {e.seconds}s.")
    except Exception as e:
        LOGGER.error(f"[Telethon] Failed to start client: {e}")

    # --- Handoff ---
    if pbot.is_connected:
        me = await pbot.get_me()
        LOGGER.info(f"[INFO] Bot running as @{me.username} | {me.first_name}")
        
        if SUPPORT_CHAT and not SUPPORT_CHAT.startswith("http"):
            try:
                target = SUPPORT_CHAT if SUPPORT_CHAT.startswith("-100") else f"@{SUPPORT_CHAT}"
                await pbot.send_photo(
                    target,
                    photo=START_IMG,
                    caption=f"✨ {BOT_NAME} ɪs ᴀʟɪᴠᴇ ʙᴀʙʏ.\n\n"
                            f"**ᴩʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ:** `{y()}`\n"
                            f"**ᴩʏʀᴏɢʀᴀᴍ ᴠᴇʀsɪᴏɴ:** `{pyrover}`\n",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("➕ Aᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ ➕", url=f"https://t.me/{me.username}?startgroup=true")
                    ]]),
                )
            except Exception as e:
                LOGGER.warning(f"Could not announce to @{SUPPORT_CHAT}: {e}")
    else:
        LOGGER.error("[CRITICAL] Pyrogram client is NOT connected. Features will be disabled.")

    LOGGER.info(f"Successfully loaded {len(ALL_MODULES)} modules.")
    LOGGER.info("Bot is running. Press Ctrl+C to stop.")
    
    await idle()
    
    if pbot.is_connected:
        await pbot.stop()
    if telethn.is_connected():
        await telethn.disconnect()
    await QueenNoxi.aiohttpsession.close()

if __name__ == "__main__":
    asyncio.run(main())
