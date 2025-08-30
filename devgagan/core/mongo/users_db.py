# devgagan/core/mongo/users_db.py

from . import users_col

# Add user (if not exists)
async def add_user(user_id: int, username: str = None) -> bool:
    user = await users_col.find_one({"user_id": user_id})
    if not user:
        await users_col.insert_one({
            "user_id": user_id,
            "username": username,
        })
        return True   # New user added
    return False      # Already exists

# Get single user
async def get_user(user_id: int):
    return await users_col.find_one({"user_id": user_id})

# Get all users (returns list of dicts)
async def get_users():
    return [doc async for doc in users_col.find({})]
