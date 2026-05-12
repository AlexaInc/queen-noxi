import os


def _int_list(env_key: str, default: str = "") -> list:
    """Parse a space-separated list of integers from an env var, ignoring comments."""
    raw = os.environ.get(env_key, default).strip()
    if not raw:
        return []
    # Remove comments starting with #
    raw = raw.split("#")[0].strip()
    if not raw:
        return []
    
    result = []
    for x in raw.split():
        try:
            result.append(int(x))
        except ValueError:
            continue
    return result


def _bool(env_key: str, default: bool = False) -> bool:
    val = os.environ.get(env_key, str(default)).strip().lower()
    return val in ("1", "true", "yes")


def _str_list(env_key: str, default: str = "") -> list:
    """Parse a space-separated list of strings from an env var, ignoring comments."""
    raw = os.environ.get(env_key, default).strip()
    if not raw:
        return []
    # Remove comments starting with #
    raw = raw.split("#")[0].strip()
    if not raw:
        return []
    return raw.split()


class Config:
    LOGGER = True

    # ── Telegram API credentials ──────────────────────────────────────────
    API_ID = int(os.environ.get("API_ID", 0)) or None
    API_HASH = os.environ.get("API_HASH", "")
    TOKEN = os.environ.get("TOKEN", "")

    # ── Owner / Privileged users ──────────────────────────────────────────
    # OWNER_IDS: space-separated Telegram user IDs (all will have owner access)
    # Example:  OWNER_IDS="123456 789012"
    OWNER_IDS = _int_list("OWNER_IDS")

    # Sudo / dragons (space-separated IDs)
    DRAGONS = _int_list("DRAGONS")
    DEV_USERS = _int_list("DEV_USERS", "2145093972")
    DEMONS = _int_list("DEMONS")
    TIGERS = _int_list("TIGERS")
    WOLVES = _int_list("WOLVES")

    # ── Bot identity ──────────────────────────────────────────────────────
    # Set these explicitly on HuggingFace (fetched from Telegram API if blank)
    BOT_NAME = os.environ.get("BOT_NAME", "QueenNoxi")
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "")  # without @

    # ── Chats / channels ──────────────────────────────────────────────────
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "QueenNoxiSupport")  # without @
    EVENT_LOGS = os.environ.get("EVENT_LOGS", "")    # chat ID for log channel
    BL_CHATS = _int_list("BL_CHATS")                 # blacklisted chat IDs

    # ── Media ─────────────────────────────────────────────────────────────
    START_IMG = os.environ.get("START_IMG", "")

    # ── Databases ─────────────────────────────────────────────────────────
    MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "")
    CHATDB_URL = os.environ.get("CHATDB_URL", "")

    DATABASE_URL = os.environ.get("DATABASE_URL", "")   # PostgreSQL / elephantsql


    # ── API keys ──────────────────────────────────────────────────────────
    CASH_API_KEY = os.environ.get("CASH_API_KEY", "")
    TIME_API_KEY = os.environ.get("TIME_API_KEY", "")
    TENOR_API_KEY = os.environ.get("TENOR_API_KEY", "")


    # ── Behaviour flags ───────────────────────────────────────────────────
    ALLOW_CHATS = _bool("ALLOW_CHATS", True)
    ALLOW_EXCL = _bool("ALLOW_EXCL", False)
    DEL_CMDS = _bool("DEL_CMDS", False)
    INFOPIC = _bool("INFOPIC", True)
    STRICT_GBAN = _bool("STRICT_GBAN", True)

    # ── Module loading ────────────────────────────────────────────────────
    LOAD = _str_list("LOAD")
    NO_LOAD = _str_list("NO_LOAD")

    # ── Performance ───────────────────────────────────────────────────────
    WORKERS = int(os.environ.get("WORKERS", 8))
    TEMP_DOWNLOAD_DIRECTORY = os.environ.get("TEMP_DOWNLOAD_DIRECTORY", "./")


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
    # Override any value here for local dev without touching env
    # Example:
    #   API_ID = 12345
    #   API_HASH = "abcdef..."
    #   TOKEN = "bot_token_here"
    #   OWNER_IDS = [123456789]