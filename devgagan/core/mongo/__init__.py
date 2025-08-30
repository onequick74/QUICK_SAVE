# devgagan/core/mongo/__init__.py

from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB

# MongoDB connection
mongo_client = AsyncIOMotorClient(MONGO_DB)
db = mongo_client["telegram_bot"]

# Collections
users_col = db["users"]
plans_col = db["plans"]
tokens_col = db["tokens"]
