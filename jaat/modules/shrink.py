from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random, string, aiohttp
from jaat import app
from jaat.core.func import *
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB, WEBSITE_URL, AD_API  

tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]
token = tdb["tokens"]

async def create_ttl_index():
    await token.create_index("expires_at", expireAfterSeconds=0)

Param = {}

async def generate_random_param(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def get_shortened_url(deep_link):
    api_url = f"https://{WEBSITE_URL}/api?api={AD_API}&url={deep_link}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()   
                if data.get("status") == "success":
                    return data.get("shortenedUrl")
    return None

async def is_user_verified(user_id):
    session = await token.find_one({"user_id": user_id})
    return session is not None

@app.on_message(filters.command("start"))
async def token_handler(client, message):
    join = await subscribe(client, message)
    if join == 1:
        return

    chat_id = "JAAT_ONE"
    msg = await app.get_messages(chat_id, 4)
    user_id = message.chat.id

    # Normal /start without param
    if len(message.command) <= 1:
        join_button = InlineKeyboardButton("Join Channel", url="https://t.me/jaat_one")
        premium = InlineKeyboardButton("Get Premium", url="https://t.me/star_jaat_bot")   
        keyboard = InlineKeyboardMarkup([[join_button],[premium]])
         
        await message.reply_photo(
            msg.photo.file_id,
            caption=(
                "Hi 👋 Welcome!\n\n"
                "✳️ I can save posts from channels or groups where forwarding is off.\n"
                "✳️ I can also download videos/audio from YT, Insta, and more.\n"
                "✳️ Just send the post link of a public channel. For private, use /login.\n"
                "✳️ Use /help to know more."
            ),
            reply_markup=keyboard
        )
        return  

    # /start with param (verification)
    param = message.command[1]
    freecheck = await chk_user(message, user_id)
    if freecheck != 1:
        await message.reply("You are a premium user no need of token 😉")
        return

    if user_id in Param and Param[user_id] == param:
        await token.insert_one({
            "user_id": user_id,
            "param": param,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=3),
        })
        del Param[user_id]   
        await message.reply("✅ You have been verified successfully! Enjoy your session for next 3 hours.")
    else:
        await message.reply("❌ Invalid or expired verification link. Please generate a new token.")

@app.on_message(filters.command("token"))
async def smart_handler(client, message):
    user_id = message.chat.id
    freecheck = await chk_user(message, user_id)

    if freecheck != 1:
        await message.reply("You are a premium user no need of token 😉")
        return

    if await is_user_verified(user_id):
        await message.reply("✅ Your free session is already active, enjoy!")
        return
         
    param = await generate_random_param()
    Param[user_id] = param   
    deep_link = f"https://t.me/{client.me.username}?start={param}"
    shortened_url = await get_shortened_url(deep_link)

    if not shortened_url:
        await message.reply("❌ Failed to generate the token link. Please try again.")
        return
         
    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Verify the token now...", url=shortened_url)]]
    )
    await message.reply(
        "Click the button below to verify your free access token:\n\n"
        "> Benefits of Free Token:\n"
        "1. No time bound up to 3 hours\n"
        "2. Batch command limit = FreeLimit + 20\n"
        "3. All functions unlocked 🚀",
        reply_markup=button
                                 )
