from pyrogram import filters
from jaat import app
from jaat.core.mongo.users_db import add_user, get_users
from config import OWNER_ID

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def bot_stats(_, message):
    """Owner ke liye total users ka stats."""
    users = await get_users()
    await message.reply_text(f"📊 Total Users: **{len(users)}**")

@app.on_message(filters.private & ~filters.command(["start", "help", "id"]))
async def auto_add_user(_, message):
    """Jab koi bhi user private me msg karega to DB me add ho jayega."""
    await add_user(message.from_user.id)
