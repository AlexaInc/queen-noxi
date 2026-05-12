import asyncio
from functools import wraps
from time import perf_counter

from cachetools import TTLCache
from pyrogram import enums
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import RPCError

from QueenNoxi import (
    DEL_CMDS,
    DEMONS,
    DEV_USERS,
    DRAGONS,
    SUPPORT_CHAT,
    TIGERS,
    WOLVES,
    pbot,
    LOGGER,
)

# stores admins in memory for 10 min.
ADMIN_CACHE = TTLCache(maxsize=512, ttl=60 * 10, timer=perf_counter)

def get_user_chat(update):
    if isinstance(update, CallbackQuery):
        return update.from_user, update.message.chat if update.message else None
    return update.from_user, update.chat


async def is_whitelist_plus(chat_id: int, user_id: int) -> bool:
    return any(user_id in user for user in [WOLVES, TIGERS, DEMONS, DRAGONS, DEV_USERS])


async def is_support_plus(chat_id: int, user_id: int) -> bool:
    return user_id in DEMONS or user_id in DRAGONS or user_id in DEV_USERS


async def is_sudo_plus(chat_id: int, user_id: int) -> bool:
    return user_id in DRAGONS or user_id in DEV_USERS


async def get_admin_ids(chat_id: int) -> list[int]:
    """Fetch from cache or API."""
    if chat_id in ADMIN_CACHE:
        return ADMIN_CACHE[chat_id]
    
    try:
        admins = []
        async for m in pbot.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if m.user:
                admins.append(m.user.id)
            elif m.status == enums.ChatMemberStatus.OWNER:
                 pass
        ADMIN_CACHE[chat_id] = admins
        return admins
    except Exception:
        return []


async def is_user_admin(chat, user_id: int) -> bool:
    if (
        chat.type == enums.ChatType.PRIVATE
        or user_id in DRAGONS
        or user_id in DEV_USERS
        or user_id in [777000, 1087968824]
    ):
        return True
    
    try:
        member = await pbot.get_chat_member(chat.id, user_id)
        if member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
            return True
    except Exception:
        pass

    admin_ids = await get_admin_ids(chat.id)
    return user_id in admin_ids


async def is_bot_admin(chat, bot_id: int) -> bool:
    if chat.type == enums.ChatType.PRIVATE:
        return True
    
    try:
        member = await pbot.get_chat_member(chat.id, bot_id)
        return member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER)
    except Exception:
        return False


def dev_plus(func):
    @wraps(func)
    async def is_dev_plus_func(client, message, *args, **kwargs):
        user, chat = get_user_chat(message)
        if user and user.id in DEV_USERS:
            return await func(client, message, *args, **kwargs)
        elif not user and chat and chat.type != enums.ChatType.PRIVATE:
            return await func(client, message, *args, **kwargs)
        else:
            LOGGER.info(f"[PERM] dev_plus denied for {user.id if user else 'Anonymous'}")
            if DEL_CMDS and hasattr(message, "text") and message.text and " " not in message.text:
                try: await message.delete()
                except: pass
            if hasattr(message, "reply_text"):
                await message.reply_text("This is a developer restricted command.")
            elif hasattr(message, "answer"):
                await message.answer("Developer restricted.", show_alert=True)

    return is_dev_plus_func


def sudo_plus(func):
    @wraps(func)
    async def is_sudo_plus_func(client, message, *args, **kwargs):
        user, chat = get_user_chat(message)

        if user and chat and await is_sudo_plus(chat.id, user.id):
            return await func(client, message, *args, **kwargs)
        elif not user and chat and chat.type != enums.ChatType.PRIVATE:
             return await func(client, message, *args, **kwargs)
        else:
            LOGGER.info(f"[PERM] sudo_plus denied for {user.id if user else 'Anonymous'}")
            if DEL_CMDS and hasattr(message, "text") and message.text and " " not in message.text:
                try: await message.delete()
                except: pass
            if hasattr(message, "reply_text"):
                await message.reply_text("Who dis non-admin telling me what to do?")
            elif hasattr(message, "answer"):
                await message.answer("Not allowed.", show_alert=True)

    return is_sudo_plus_func


def support_plus(func):
    @wraps(func)
    async def is_support_plus_func(client, message, *args, **kwargs):
        user, chat = get_user_chat(message)

        if user and chat and await is_support_plus(chat.id, user.id):
            return await func(client, message, *args, **kwargs)
        elif not user and chat and chat.type != enums.ChatType.PRIVATE:
             return await func(client, message, *args, **kwargs)
        else:
            LOGGER.info(f"[PERM] support_plus denied for {user.id if user else 'Anonymous'}")
            if hasattr(message, "reply_text"):
                await message.reply_text("This is for support users only.")
            elif hasattr(message, "answer"):
                await message.answer("Support users only.", show_alert=True)

    return is_support_plus_func


def whitelist_plus(func):
    @wraps(func)
    async def is_whitelist_plus_func(client, message, *args, **kwargs):
        user, chat = get_user_chat(message)

        if user and chat and await is_whitelist_plus(chat.id, user.id):
            return await func(client, message, *args, **kwargs)
        elif not user and chat and chat.type != enums.ChatType.PRIVATE:
             return await func(client, message, *args, **kwargs)
        else:
            LOGGER.info(f"[PERM] whitelist_plus denied for {user.id if user else 'Anonymous'}")
            if hasattr(message, "reply_text"):
                await message.reply_text(f"You don't have access to use this.\nVisit @{SUPPORT_CHAT}")
            elif hasattr(message, "answer"):
                await message.answer("No access.", show_alert=True)

    return is_whitelist_plus_func


def user_admin(func):
    @wraps(func)
    async def is_admin(client, message, *args, **kwargs):
        user, chat = get_user_chat(message)

        if user and chat and await is_user_admin(chat, user.id):
            return await func(client, message, *args, **kwargs)
        elif not user and chat and chat.type != enums.ChatType.PRIVATE:
            return await func(client, message, *args, **kwargs)
        else:
            LOGGER.info(f"[PERM] user_admin denied for {user.id if user else 'Anonymous'}")
            if DEL_CMDS and hasattr(message, "text") and message.text and " " not in message.text:
                try: await message.delete()
                except: pass
            if hasattr(message, "reply_text"):
                await message.reply_text("Who dis non-admin telling me what to do?")
            elif hasattr(message, "answer"):
                await message.answer("Admin required.", show_alert=True)

    return is_admin


def user_admin_no_reply(func):
    @wraps(func)
    async def is_not_admin_no_reply(client, message, *args, **kwargs):
        user, chat = get_user_chat(message)

        if user and chat and await is_user_admin(chat, user.id):
            return await func(client, message, *args, **kwargs)
        elif not user and chat and chat.type != enums.ChatType.PRIVATE:
            return await func(client, message, *args, **kwargs)
        else:
            LOGGER.info(f"[PERM] user_admin_no_reply denied for {user.id if user else 'Anonymous'}")
            if hasattr(message, "answer"):
                await message.answer("Admin required.", show_alert=True)

    return is_not_admin_no_reply


def user_not_admin(func):
    @wraps(func)
    async def is_not_admin(client, message, *args, **kwargs):
        user, chat = get_user_chat(message)

        if user and chat and not await is_user_admin(chat, user.id):
            return await func(client, message, *args, **kwargs)
        elif not user and chat and chat.type != enums.ChatType.PRIVATE:
            return
        elif not user:
            return await func(client, message, *args, **kwargs)

    return is_not_admin


def bot_admin(func):
    @wraps(func)
    async def is_admin(client, message, *args, **kwargs):
        _, chat = get_user_chat(message)
        if not chat: return
        
        if await is_bot_admin(chat, client.me.id if hasattr(client, "me") and client.me else (await client.get_me()).id):
            return await func(client, message, *args, **kwargs)
        else:
            LOGGER.info(f"[PERM] bot_admin denied in {chat.id}")
            if hasattr(message, "reply_text"):
                await message.reply_text("I'm not admin! - REEEEEE")
            elif hasattr(message, "answer"):
                await message.answer("Bot is not admin!", show_alert=True)

    return is_admin


def can_pin(func):
    @wraps(func)
    async def pin_rights(client, message, *args, **kwargs):
        _, chat = get_user_chat(message)
        if not chat: return
        me = await pbot.get_chat_member(chat.id, client.me.id if hasattr(client, "me") and client.me else (await client.get_me()).id)

        if (me.privileges and me.privileges.can_pin_messages) or me.status == enums.ChatMemberStatus.OWNER:
            return await func(client, message, *args, **kwargs)
        else:
            LOGGER.info(f"[PERM] can_pin denied in {chat.id}")
            if hasattr(message, "reply_text"):
                 await message.reply_text("I can't pin messages here!")
            elif hasattr(message, "answer"):
                 await message.answer("I can't pin messages here!", show_alert=True)

    return pin_rights


def can_promote(func):
    @wraps(func)
    async def promote_rights(client, message, *args, **kwargs):
        _, chat = get_user_chat(message)
        if not chat: return
        me = await pbot.get_chat_member(chat.id, client.me.id if hasattr(client, "me") and client.me else (await client.get_me()).id)

        if (me.privileges and me.privileges.can_promote_members) or me.status == enums.ChatMemberStatus.OWNER:
            return await func(client, message, *args, **kwargs)
        else:
            LOGGER.info(f"[PERM] can_promote denied in {chat.id}")
            if hasattr(message, "reply_text"):
                await message.reply_text("I can't promote/demote people here!")
            elif hasattr(message, "answer"):
                await message.answer("I can't promote people here!", show_alert=True)

    return promote_rights


def can_delete(func):
    @wraps(func)
    async def delete_rights(client, message, *args, **kwargs):
        _, chat = get_user_chat(message)
        if not chat: return
        me = await pbot.get_chat_member(chat.id, client.me.id if hasattr(client, "me") and client.me else (await client.get_me()).id)

        if (me.privileges and me.privileges.can_delete_messages) or me.status == enums.ChatMemberStatus.OWNER:
            return await func(client, message, *args, **kwargs)
        else:
            LOGGER.info(f"[PERM] can_delete denied in {chat.id}")
            if hasattr(message, "reply_text"):
                await message.reply_text("I can't delete messages here!")
            elif hasattr(message, "answer"):
               await message.answer("I can't delete messages here!", show_alert=True)

    return delete_rights


async def is_user_ban_protected(chat, user_id: int, member=None) -> bool:
    if (
        chat.type == enums.ChatType.PRIVATE
        or user_id in DRAGONS
        or user_id in DEV_USERS
        or user_id in [777000, 1087968824]
    ):
        return True

    if not member:
        try: member = await pbot.get_chat_member(chat.id, user_id)
        except: return False

    return member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER)


async def is_user_in_chat(chat, user_id: int) -> bool:
    try:
        await chat.get_member(user_id)
        return True
    except Exception:
        return False


def can_restrict(func):
    @wraps(func)
    async def restrict_rights(client, message, *args, **kwargs):
        _, chat = get_user_chat(message)
        if not chat: return
        me = await pbot.get_chat_member(chat.id, client.me.id if hasattr(client, "me") and client.me else (await client.get_me()).id)

        if (me.privileges and me.privileges.can_restrict_members) or me.status == enums.ChatMemberStatus.OWNER:
            return await func(client, message, *args, **kwargs)
        else:
            LOGGER.info(f"[PERM] can_restrict denied in {chat.id}")
            if hasattr(message, "reply_text"):
                await message.reply_text("I can't restrict people here!")
            elif hasattr(message, "answer"):
               await message.answer("I can't restrict people here!", show_alert=True)

    return restrict_rights


def user_can_ban(func):
    @wraps(func)
    async def user_is_banhammer(client, message, *args, **kwargs):
        user, chat = get_user_chat(message)
        if not user:
            if chat and chat.type != enums.ChatType.PRIVATE:
                return await func(client, message, *args, **kwargs)
            return
            
        try:
            member = await pbot.get_chat_member(chat.id, user.id)
            if (
                not ((member.privileges and member.privileges.can_restrict_members) or member.status == enums.ChatMemberStatus.OWNER)
                and user.id not in DRAGONS
                and user.id not in [777000, 1087968824]
            ):
                LOGGER.info(f"[PERM] user_can_ban denied for {user.id}")
                if hasattr(message, "reply_text"):
                    await message.reply_text("😿 Sorry You can't do that")
                elif hasattr(message, "answer"):
                   await message.answer("Sorry You can't do that", show_alert=True)
                return
        except Exception:
            if user.id not in DRAGONS:
                return
                
        return await func(client, message, *args, **kwargs)

    return user_is_banhammer


def connection_status(func):
    @wraps(func)
    async def connected_status(client, message, *args, **kwargs):
        user, chat = get_user_chat(message)
        if not user:
            return await func(client, message, *args, **kwargs)

        from QueenNoxi.modules import connection
        conn = await connection.connected(client, message, user.id, need_admin=False)

        if conn:
            return await func(client, message, *args, **kwargs)
        else:
            if chat and chat.type == enums.ChatType.PRIVATE:
                LOGGER.info(f"[PERM] connection_status denied for {user.id}")
                if hasattr(message, "reply_text"):
                    await message.reply_text("Send /connect in a group first.")
                elif hasattr(message, "answer"):
                   await message.answer("Send /connect in a group.", show_alert=True)
                return 
            return await func(client, message, *args, **kwargs)

    return connected_status
