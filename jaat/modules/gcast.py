from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER_ID
from jaat.core.mongo.users_db import get_users
from jaat import app

@app.on_message(filters.command("gcast") & filters.user(OWNER_ID))
async def broadcast_message(_, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text("Usage: /gcast [message or reply to a message]")
    
    text = message.text.split(None, 1)[1] if len(message.command) >= 2 else None
    reply = message.reply_to_message
    
    sent = 0
    failed = 0
    
    users = await get_users()
    for user_id in users:
        try:
            if reply:
                await reply.copy(user_id)
            elif text:
                await app.send_message(user_id, text)
            sent += 1
        except Exception:
            failed += 1
    
    await message.reply_text(f"✅ Broadcast completed\n\n👤 Sent: {sent}\n❌ Failed: {failed}")
