from QueenNoxi.modules.no_sql import QueenNoxidb

usersdb = QueenNoxidb.served_users

async def is_served_user(user_id: int) -> bool:
    user = await usersdb.find_one({"user_id": user_id})
    return user is not None

async def get_served_users() -> list:
    users_list = []
    async for user in usersdb.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list

async def save_id(user_id: int):
    if await is_served_user(user_id):
        return
    await usersdb.insert_one({"user_id": user_id})

async def remove_served_users(user_id: int):
    await usersdb.delete_one({"user_id": user_id})
