# devgagan/core/mongo/__init__.py

from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB
import asyncio, logging

# Logger
logger = logging.getLogger(__name__)

# MongoDB connection
try:
    mongo_client = AsyncIOMotorClient(MONGO_DB, serverSelectionTimeoutMS=5000)
    db = mongo_client["telegram_bot"]

    # Collections
    users_col = db["users"]
    plans_col = db["plans"]
    tokens_col = db["tokens"]

    # Run a quick ping test at startup (non-blocking)
    async def _ping():
        try:
            await db.command("ping")
            logger.info("✅ MongoDB connected successfully.")
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")

    asyncio.get_event_loop().create_task(_ping())

except Exception as e:
    logger.error(f"❌ MongoDB init error: {e}")
    mongo_client, db, users_col, plans_col, tokens_col = None, None, None, None, None
