# STAR JAAT 

import asyncio
import logging
import time
from pyrogram import Client
from pyrogram.enums import ParseMode 
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB, DEFAULT_SESSION
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from motor.motor_asyncio import AsyncIOMotorClient

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

botStartTime = time.time()

# ---------------- Pyrogram Bot ----------------
app = Client(
    "pyrobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=50,
    parse_mode=ParseMode.MARKDOWN
)

# ---------------- Telethon Bot (with StringSession) ----------------
# FloodWait se bachane ke liye StringSession use kiya gaya hai
TELETHON_SESSION = "telethon_session_string"  # <-- isko ek baar generate karke config me save kar lena

if TELETHON_SESSION:
    sex = TelegramClient(StringSession(TELETHON_SESSION), API_ID, API_HASH)
else:
    sex = TelegramClient(StringSession(), API_ID, API_HASH).start(bot_token=BOT_TOKEN)
    print("⚠️ Telethon StringSession generate kar lena aur config me daalna zaruri hai.")

# ---------------- Pyrogram Userbot (STRING se) ----------------
if STRING:
    pro = Client("ggbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)
else:
    pro = None

# ---------------- Optional Default Session ----------------
if DEFAULT_SESSION:
    userrbot = Client("userrbot", api_id=API_ID, api_hash=API_HASH, session_string=DEFAULT_SESSION)
else:
    userrbot = None

# ---------------- MongoDB Setup ----------------
tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]  # Your database
token = tdb["tokens"]  # Your tokens collection

async def create_ttl_index():
    """Ensure the TTL index exists for the `tokens` collection."""
    await token.create_index("expires_at", expireAfterSeconds=0)

async def setup_database():
    await create_ttl_index()
    print("MongoDB TTL index created.")

# ---------------- Restrict Bot ----------------
async def restrict_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    await setup_database()
    await app.start()
    getme = await app.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    BOT_NAME = f"{getme.first_name} {getme.last_name}" if getme.last_name else getme.first_name
    
    if pro:
        await pro.start()
    if userrbot:
        await userrbot.start()
    await sex.start(bot_token=BOT_TOKEN)  # Start Telethon Bot with token (only once)

loop.run_until_complete(restrict_bot())
