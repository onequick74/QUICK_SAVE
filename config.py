import os

# Required (get these from https://my.telegram.org)
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

# Your bot token from BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Optional: Pyrogram user session strings
STRING = os.getenv("STRING", "")               # userbot (pyrogram)
DEFAULT_SESSION = os.getenv("DEFAULT_SESSION", "")

# Optional: Telethon StringSession for the bot client (prevents FloodWait loops)
# Generate once with scripts/generate_telethon_session.py then paste here/env.
TELETHON_SESSION = os.getenv("TELETHON_SESSION", "")

# Mongo
MONGO_DB = os.getenv("MONGO_DB", "mongodb://localhost:27017")

# Logging / Ownership
LOG_GROUP = int(os.getenv("LOG_GROUP", "0"))   # e.g. -1001234567890
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
