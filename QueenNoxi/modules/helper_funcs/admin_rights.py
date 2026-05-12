from pyrogram import enums
from QueenNoxi import pbot

async def user_can_promote(chat_id: int, user_id: int) -> bool:
    try:
        member = await pbot.get_chat_member(chat_id, user_id)
        return member.status == enums.ChatMemberStatus.OWNER or (member.privileges and member.privileges.can_promote_members)
    except Exception:
        return False


async def user_can_ban(chat_id: int, user_id: int) -> bool:
    try:
        member = await pbot.get_chat_member(chat_id, user_id)
        return member.status == enums.ChatMemberStatus.OWNER or (member.privileges and member.privileges.can_restrict_members)
    except Exception:
        return False


async def user_can_pin(chat_id: int, user_id: int) -> bool:
    try:
        member = await pbot.get_chat_member(chat_id, user_id)
        return member.status == enums.ChatMemberStatus.OWNER or (member.privileges and member.privileges.can_pin_messages)
    except Exception:
        return False


async def user_can_changeinfo(chat_id: int, user_id: int) -> bool:
    try:
        member = await pbot.get_chat_member(chat_id, user_id)
        return member.status == enums.ChatMemberStatus.OWNER or (member.privileges and member.privileges.can_change_info)
    except Exception:
        return False
