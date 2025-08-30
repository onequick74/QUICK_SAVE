# devgagan/core/mongo/users_db.py

from . import users_col

async def add_user(user_id: int, username: str = None):
    user = await users_col.find_one({"user_id": user_id})
    if not user:
        await users_col.insert_one({
            "user_id": user_id,
            "username": username,
        })
    return True

async def get_user(user_id: int):
    return await users_col.find_one({"user_id": user_id})

async def get_users():
    return users_col.find({})
