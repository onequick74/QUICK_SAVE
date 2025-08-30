from config import MONGO_DB
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli

mongo = MongoCli(MONGO_DB)
_database = mongo.user_data
_collection = _database.users_data_db

async def get_data(user_id):
    """Return the user's document or None."""
    return await _collection.find_one({"_id": user_id})

async def set_thumbnail(user_id, thumb):
    """Set or update thumbnail path for a user."""
    await _collection.update_one(
        {"_id": user_id},
        {"$set": {"thumb": thumb}},
        upsert=True
    )

async def set_caption(user_id, caption):
    """Set or update default caption for a user."""
    await _collection.update_one(
        {"_id": user_id},
        {"$set": {"caption": caption}},
        upsert=True
    )

async def replace_caption(user_id, replace_txt, to_replace):
    """Store replacement mapping for captions (two fields)."""
    await _collection.update_one(
        {"_id": user_id},
        {"$set": {"replace_txt": replace_txt, "to_replace": to_replace}},
        upsert=True
    )

async def set_session(user_id, session):
    """Save exported session string for a user (for userbot)."""
    await _collection.update_one(
        {"_id": user_id},
        {"$set": {"session": session}},
        upsert=True
    )

async def clean_words(user_id, new_clean_words):
    """Add new words to clean_words list (keeps unique entries)."""
    if not isinstance(new_clean_words, list):
        new_clean_words = [new_clean_words]
    await _collection.update_one(
        {"_id": user_id},
        {"$addToSet": {"clean_words": {"$each": new_clean_words}}},
        upsert=True
    )

async def remove_clean_words(user_id, words_to_remove):
    """Remove given words from the user's clean_words list."""
    if not isinstance(words_to_remove, list):
        words_to_remove = [words_to_remove]
    await _collection.update_one(
        {"_id": user_id},
        {"$pullAll": {"clean_words": words_to_remove}}
    )

async def set_channel(user_id, chat_id):
    """Set user's preferred/target chat_id."""
    await _collection.update_one(
        {"_id": user_id},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )

async def all_words_remove(user_id):
    """Clear all clean_words for a user."""
    await _collection.update_one(
        {"_id": user_id},
        {"$set": {"clean_words": []}}
    )

async def remove_thumbnail(user_id):
    """Remove thumbnail field."""
    await _collection.update_one({"_id": user_id}, {"$unset": {"thumb": ""}})

async def remove_caption(user_id):
    """Remove caption field."""
    await _collection.update_one({"_id": user_id}, {"$unset": {"caption": ""}})

async def remove_replace(user_id):
    """Remove replace_txt and to_replace fields."""
    await _collection.update_one({"_id": user_id}, {"$unset": {"replace_txt": "", "to_replace": ""}})

async def remove_session(user_id):
    """Remove stored session string (keeps doc intact)."""
    await _collection.update_one({"_id": user_id}, {"$unset": {"session": ""}})

async def remove_channel(user_id):
    """Remove stored chat_id."""
    await _collection.update_one({"_id": user_id}, {"$unset": {"chat_id": ""}})

async def delete_session(user_id):
    """Alias to explicitly unset session field (keeps doc intact)."""
    await _collection.update_one({"_id": user_id}, {"$unset": {"session": ""}})
