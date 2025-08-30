from config import MONGO_DB
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli

mongo = MongoCli(MONGO_DB)
db = mongo.users
users_col = db.users_db

async def get_users():
    """Return list of all user IDs."""
    user_list = []
    async for user in users_col.find({"user": {"$gt": 0}}):
        user_list.append(user['user'])
    return user_list

async def get_user(user_id: int):
    """Check if user exists in DB."""
    users = await get_users()
    return user_id in users

async def add_user(user_id: int):
    """Add new user to DB if not already present."""
    users = await get_users()
    if user_id not in users:
        await users_col.insert_one({"user": user_id})

async def del_user(user_id: int):
    """Delete user from DB if exists."""
    users = await get_users()
    if user_id in users:
        await users_col.delete_one({"user": user_id})
