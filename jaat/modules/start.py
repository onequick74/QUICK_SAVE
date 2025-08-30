from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from jaat import app
from jaat.core.mongo.users_db import add_user

START_TEXT = """
👋 **Welcome {mention}!**

Main ek advanced Telegram bot hoon.  
Niche diye gaye buttons ka use karke features explore karo.
"""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("👑 Plans", callback_data="plans"),
            InlineKeyboardButton("ℹ️ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("📢 Updates", url="https://t.me/jaat_updates")
        ]
    ]
)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(_, message):
    await add_user(message.from_user.id)
    await message.reply_text(
        START_TEXT.format(mention=message.from_user.mention),
        reply_markup=START_BUTTONS,
        disable_web_page_preview=True
    )
