# STAR JAAT

import asyncio
import logging
import time
from pyrogram import Client
from pyrogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient
from telethon import TelegramClient
from telethon.sessions import StringSession

from config import (
    API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB, DEFAULT_SESSION, TELETHON_SESSION
)

# ---- event loop ----
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

# ---------------- Telethon Bot (StringSession prevents repeated ImportBotAuthorization) ----
if TELETHON_SESSION:
    sex = TelegramClient(StringSession(TELETHON_SESSION), API_ID, API_HASH)
else:
    # First run will create an in-memory session; best to generate TELETHON_SESSION and set it in env/config.
    sex = TelegramClient(StringSession(), API_ID, API_HASH)

# ---------------- Optional Pyrogram user sessions ----------------
pro = Client("ggbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING) if STRING else None
userrbot = Client("userrbot", api_id=API_ID, api_hash=API_HASH, session_string=DEFAULT_SESSION) if DEFAULT_SESSION else None

# ---------------- Mongo (motor) ----------------
tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]
token = tdb["tokens"]

async def create_ttl_index():
    await token.create_index("expires_at", expireAfterSeconds=0)

async def setup_database():
    await create_ttl_index()
    print("MongoDB TTL index created.")

async def restrict_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    await setup_database()

    # Start Pyrogram bot
    await app.start()
    me = await app.get_me()
    BOT_ID = me.id
    BOT_USERNAME = me.username
    BOT_NAME = f"{me.first_name} {me.last_name}" if me.last_name else me.first_name

    # Start optional sessions
    if pro:
        await pro.start()
    if userrbot:
        await userrbot.start()

    # Start Telethon bot ONCE (will reuse StringSession)
    await sex.start(bot_token=BOT_TOKEN)

loop.run_until_complete(restrict_bot())
