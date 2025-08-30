from pyrogram import filters
from jaat import app

@app.on_message(filters.command("id"))
async def get_id(_, message):
    if message.chat.type in ["group", "supergroup", "channel"]:
        await message.reply_text(f"Chat ID: `{message.chat.id}`")
    elif message.reply_to_message:
        await message.reply_text(f"Replied User ID: `{message.reply_to_message.from_user.id}`")
    else:
        await message.reply_text(f"Your User ID: `{message.from_user.id}`")
