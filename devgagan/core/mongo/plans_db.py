# devgagan/core/mongo/plans_db.py

from . import plans_col

async def add_premium_user(user_id: int, expires_at: int):
    await plans_col.update_one(
        {"user_id": user_id},
        {"$set": {"expires_at": expires_at}},
        upsert=True,
    )

async def premium_users():
    return plans_col.find({})
 
