from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from jaat import app
from jaat.core.mongo.db import set_session
from config import OWNER_ID

@app.on_message(filters.command("login") & filters.private)
async def login_user(_, message):
    if message.from_user.id not in OWNER_ID:
        return await message.reply_text("⛔ Ye command sirf owner ke liye available hai.")

    if len(message.command) < 2:
        return await message.reply_text("❌ Session string dena zaruri hai.\n\nUsage: `/login <SESSION_STRING>`")

    session_string = message.text.split(" ", 1)[1]

    try:
        await set_session(message.from_user.id, session_string)
        await message.reply_text(
            "✅ Session string save ho gaya hai!",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Check DB", callback_data="check_db")]]
            )
        )
    except Exception as e:
        await message.reply_text(f"⚠️ Error: `{str(e)}`")
