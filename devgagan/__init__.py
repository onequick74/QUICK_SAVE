# devgagan/__init__.py
# STAR JAAT (fixed)

import asyncio
import logging
import time
import os

from pyrogram import Client
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB, DEFAULT_SESSION
from telethon import TelegramClient
from motor.motor_asyncio import AsyncIOMotorClient

# -------------------
# Logging setup
# -------------------
logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

botStartTime = time.time()

# -------------------
# Main Pyrogram bot
# -------------------
app = Client(
    "pyrobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=50,
    parse_mode=ParseMode.MARKDOWN,
)

# -------------------
# Telethon client (single bot session)
# -------------------
telethon_client = TelegramClient("telethon_bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# -------------------
# Optional userbots
# -------------------
pro = None
if STRING:
    pro = Client("ggbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)

userrbot = None
if DEFAULT_SESSION:
    userrbot = Client("userrbot", api_id=API_ID, api_hash=API_HASH, session_string=DEFAULT_SESSION)

# -------------------
# MongoDB init
# -------------------
tclient, tdb = None, None
if MONGO_DB:
    tclient = AsyncIOMotorClient(MONGO_DB)
    tdb = tclient["telegram_bot"]

# -------------------
# Bot identity setup
# -------------------
BOT_ID, BOT_USERNAME, BOT_NAME = None, None, None


async def restrict_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME

    me = await app.get_me()
    BOT_ID = me.id
    BOT_USERNAME = me.username
    BOT_NAME = " ".join(x for x in [me.first_name, me.last_name] if x)

    if pro:
        await pro.start()
    if userrbot:
        await userrbot.start()


# -------------------
# Startup
# -------------------
async def startup():
    await app.start()
    await restrict_bot()


# Ensure event loop runs startup
loop = asyncio.get_event_loop()
loop.run_until_complete(startup())
