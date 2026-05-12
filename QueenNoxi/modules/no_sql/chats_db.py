from QueenNoxi.modules.no_sql import QueenNoxidb

chatsdb = QueenNoxidb.served_chats

async def get_served_chats() -> list:
    chats_list = []
    async for chat in chatsdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat)
    return chats_list

async def is_served_chat(chat_id: int) -> bool:
    chat = await chatsdb.find_one({"chat_id": chat_id})
    return chat is not None

async def add_served_chat(chat_id: int):
    if await is_served_chat(chat_id):
        return
    await chatsdb.insert_one({"chat_id": chat_id})

async def remove_served_chat(chat_id: int):
    await chatsdb.delete_one({"chat_id": chat_id})
