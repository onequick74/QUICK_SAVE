from config import MONGO_DB
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli

mongo = MongoCli(MONGO_DB)
db = mongo.users
db = db.users_db

async def get_users():
    user_list = []
    async for user in db.users.find({"user": {"$gt": 0}}):
        user_list.append(user['user'])
    return user_list

async def get_user(user):
    users = await get_users()
    return user in users

async def add_user(user):
    users = await get_users()
    if user not in users:
        await db.users.insert_one({"user": user})

async def del_user(user):
    users = await get_users()
    if user in users:
        await db.users.delete_one({"user": user})
