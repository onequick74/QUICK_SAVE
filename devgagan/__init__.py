# devgagan/__init__.py
# STAR JAAT

import asyncio
import logging
import time
from pyrogram import Client
from pyrogram.enums import ParseMode 
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB, DEFAULT_SESSION
from telethon.sync import TelegramClient
from motor.motor_asyncio import AsyncIOMotorClient

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

botStartTime = time.time()

# Pyrogram bot client
app = Client(
    "pyrobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=50,
    parse_mode=ParseMode.MARKDOWN
)

# Telethon client
sex = TelegramClient('sexrepo', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Pyrogram userbot (optional)
if STRING:
    pro = Client("ggbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)
else:
    pro = None

if DEFAULT_SESSION:
    userrbot = Client("userrbot", api_id=API_ID, api_hash=API_HASH, session_string=DEFAULT_SESSION)
else:
    userrbot = None

# Telethon (second session for utility work)
telethon_client = TelegramClient('telethon_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# MongoDB setup (moved to core/mongo)
tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]  

async def restrict_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    getme = await app.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    BOT_NAME = f"{getme.first_name} {getme.last_name}" if getme.last_name else getme.first_name
    
    if pro:
        await pro.start()
    if userrbot:
        await userrbot.start()

loop.run_until_complete(app.start())
loop.run_until_complete(restrict_bot())
