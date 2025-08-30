import datetime
from config import MONGO_DB
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli

mongo = MongoCli(MONGO_DB)
plans_db = mongo.plans
plans_col = plans_db.plans_col

async def add_user_plan(user_id: int, plan: str, duration_days: int):
    """Add a new plan for a user with expiry date."""
    expiry_date = datetime.datetime.utcnow() + datetime.timedelta(days=duration_days)
    await plans_col.update_one(
        {"user_id": user_id},
        {"$set": {"plan": plan, "expiry_date": expiry_date}},
        upsert=True
    )

async def get_user_plan(user_id: int):
    """Get plan info for a user (dict with plan & expiry_date)."""
    return await plans_col.find_one({"user_id": user_id})

async def remove_user_plan(user_id: int):
    """Remove a user's plan entry."""
    await plans_col.delete_one({"user_id": user_id})

async def check_and_remove_expired_users():
    """Auto-remove expired users (runs every hour via __main__)."""
    now = datetime.datetime.utcnow()
    expired_users = plans_col.find({"expiry_date": {"$lte": now}})
    async for user in expired_users:
        await plans_col.delete_one({"user_id": user["user_id"]})
        print(f"[INFO] Removed expired user: {user['user_id']}")

async def premium_users():
    """Return list of user_ids who have active premium plan."""
    now = datetime.datetime.utcnow()
    user_list = []
    async for user in plans_col.find({"expiry_date": {"$gt": now}}):
        user_list.append(user["user_id"])
    return user_list
