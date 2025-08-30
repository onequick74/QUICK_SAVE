import os

# Telegram API (https://my.telegram.org)
API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "")

# Bot token from @BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# MongoDB connection (Mongo Atlas recommended)
MONGO_DB = os.environ.get("MONGO_DB", "")

# Optional userbot sessions
STRING = os.environ.get("STRING", None)             # Premium userbot
DEFAULT_SESSION = os.environ.get("DEFAULT_SESSION", None)  # Fallback userbot

# Bot owner & logging
OWNER_ID = list(map(int, os.environ.get("OWNER_ID", "123456789").split()))
LOG_GROUP = int(os.environ.get("LOG_GROUP", "-100123456789"))

# Force-subscribe channel (optional)
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-100123456789")) if os.environ.get("CHANNEL_ID") else None

# Upload limits
FREEMIUM_LIMIT = int(os.environ.get("FREEMIUM_LIMIT", "5"))      # free users
PREMIUM_LIMIT = int(os.environ.get("PREMIUM_LIMIT", "50"))       # premium users

# App name (branding)
BOT_NAME = os.environ.get("BOT_NAME", "Star Jaat Uploader Bot")
