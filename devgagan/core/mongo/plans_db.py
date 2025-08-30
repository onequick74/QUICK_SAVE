# devgagan/core/mongo/plans_db.py

import time
from . import plans_col

# Add / Update a premium user with expiry timestamp
async def add_premium_user(user_id: int, expires_at: int):
    await plans_col.update_one(
        {"user_id": user_id},
        {"$set": {"expires_at": expires_at}},
        upsert=True,
    )

# Get all premium users (list of dicts)
async def premium_users():
    return [doc async for doc in plans_col.find({})]

# Check & remove expired users
async def check_and_remove_expired_users():
    now = int(time.time())
    async for user in plans_col.find({}):
        if user.get("expires_at") and user["expires_at"] < now:
            await plans_col.delete_one({"user_id": user["user_id"]})
            print(f"⏳ Removed expired premium user: {user['user_id']}")
