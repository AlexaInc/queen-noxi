from typing import List, Optional, Tuple

from pyrogram.types import Message
from pyrogram import enums

from QueenNoxi import LOGGER, pbot
from QueenNoxi.modules.users import get_user_id


async def id_from_reply(message: Message) -> Tuple[Optional[int], Optional[str]]:
    prev_message = message.reply_to_message
    if not prev_message:
        return None, None
    user_id = prev_message.from_user.id
    res = message.text.split(None, 1)
    if len(res) < 2:
        return user_id, ""
    return user_id, res[1]


async def extract_user(message: Message, args: List[str]) -> Optional[int]:
    user_id, _ = await extract_user_and_text(message, args)
    return user_id


async def extract_user_and_text(
    message: Message, args: List[str]
) -> Tuple[Optional[int], Optional[str]]:
    prev_message = message.reply_to_message
    split_text = message.text.split(None, 1)

    if len(split_text) < 2:
        return await id_from_reply(message)

    text_to_parse = split_text[1]
    text = ""
    user_id = None

    # Check for text mention entities
    if message.entities:
        for ent in message.entities:
            if ent.type == enums.MessageEntityType.TEXT_MENTION:
                user_id = ent.user.id
                text = message.text[ent.offset + ent.length :].strip()
                break

    if user_id:
        pass
    elif len(args) >= 1 and args[0][0] == "@":
        user_name = args[0]
        user_id = get_user_id(user_name)
        if not user_id:
            try:
                user = await pbot.get_users(user_name)
                user_id = user.id
            except Exception:
                await message.reply_text(
                    "No idea who this user is. You'll be able to interact with them if "
                    "you reply to that person's message instead, or forward one of that user's messages."
                )
                return None, None

        res = message.text.split(None, 2)
        if len(res) >= 3:
            text = res[2]

    elif len(args) >= 1 and args[0].isdigit():
        user_id = int(args[0])
        res = message.text.split(None, 2)
        if len(res) >= 3:
            text = res[2]

    elif prev_message:
        user_id, text = await id_from_reply(message)

    else:
        return None, None


    return user_id, text




def extract_text(message: Message) -> str:
    return (
        message.text
        or message.caption
        or (message.sticker.emoji if message.sticker else None)
    )


async def extract_unt_fedban(
    message: Message, args: List[str]
) -> Tuple[Optional[int], Optional[str]]:
    # Fedban extraction is often similar or same as standard extraction
    return await extract_user_and_text(message, args)


async def extract_user_fban(message: Message, args: List[str]) -> Optional[int]:
    user_id, _ = await extract_unt_fedban(message, args)
    return user_id
