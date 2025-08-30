# devgagan/core/mongo/db.py
# STAR JAAT
# ---------------------------------------------------

from config import MONGO_DB
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli

# MongoDB setup
mongo = MongoCli(MONGO_DB)
db = mongo["user_data"]          # Database
users_col = db["users_data_db"]  # Collection

# ----------------- Functions ----------------- #

async def get_data(user_id):
    return await users_col.find_one({"_id": user_id})

async def set_thumbnail(user_id, thumb):
    await users_col.update_one({"_id": user_id}, {"$set": {"thumb": thumb}}, upsert=True)

async def set_caption(user_id, caption):
    await users_col.update_one({"_id": user_id}, {"$set": {"caption": caption}}, upsert=True)

async def replace_caption(user_id, replace_txt, to_replace):
    await users_col.update_one(
        {"_id": user_id}, 
        {"$set": {"replace_txt": replace_txt, "to_replace": to_replace}}, 
        upsert=True
    )

async def set_session(user_id, session):
    await users_col.update_one({"_id": user_id}, {"$set": {"session": session}}, upsert=True)

async def clean_words(user_id, new_clean_words):
    data = await get_data(user_id)
    existing_words = data.get("clean_words", []) if data else []
    updated_words = list(set(existing_words + new_clean_words))
    await users_col.update_one({"_id": user_id}, {"$set": {"clean_words": updated_words}}, upsert=True)

async def remove_clean_words(user_id, words_to_remove):
    data = await get_data(user_id)
    existing_words = data.get("clean_words", []) if data else []
    updated_words = [word for word in existing_words if word not in words_to_remove]
    await users_col.update_one({"_id": user_id}, {"$set": {"clean_words": updated_words}}, upsert=True)

async def set_channel(user_id, chat_id):
    await users_col.update_one({"_id": user_id}, {"$set": {"chat_id": chat_id}}, upsert=True)

async def all_words_remove(user_id):
    await users_col.update_one({"_id": user_id}, {"$set": {"clean_words": None}})

async def remove_thumbnail(user_id):
    await users_col.update_one({"_id": user_id}, {"$set": {"thumb": None}})

async def remove_caption(user_id):
    await users_col.update_one({"_id": user_id}, {"$set": {"caption": None}})

async def remove_replace(user_id):
    await users_col.update_one({"_id": user_id}, {"$set": {"replace_txt": None, "to_replace": None}})

async def remove_session(user_id):
    await users_col.update_one({"_id": user_id}, {"$set": {"session": None}})

async def remove_channel(user_id):
    await users_col.update_one({"_id": user_id}, {"$set": {"chat_id": None}})

async def delete_session(user_id):
    """Delete the session associated with the given user_id from the database."""
    await users_col.update_one({"_id": user_id}, {"$unset": {"session": ""}})
