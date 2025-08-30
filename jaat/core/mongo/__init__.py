from config import MONGO_DB
from motor.motor_asyncio import AsyncIOMotorClient

# Initialize Mongo connection
mongo_client = AsyncIOMotorClient(MONGO_DB)

# Default database for bot
db = mongo_client.bot_db
