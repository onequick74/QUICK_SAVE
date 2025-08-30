from pyrogram import filters
from devgagan import app
from devgagan.core.get_func import get_msg, upload_media

# Example: reply /save with a media to forward it to a chat id
TARGET_CHAT = 0  # <- put your channel/chat id here (e.g. -1001234567890)

@app.on_message(filters.command(["save", "upload"]) & filters.reply)
async def save_handler(client, message):
    if TARGET_CHAT == 0:
        return await message.reply_text("Set TARGET_CHAT in devgagan/modules/main.py")

    reply = message.reply_to_message
    if not reply or not (reply.video or reply.document or reply.photo):
        return await message.reply_text("Reply to a video/photo/document!")

    path = await reply.download()
    cap = (await get_msg(message)) or ""
    edit = await message.reply_text("Starting upload…")
    topic_id = None  # set thread id here if needed

    try:
        await upload_media(message.from_user.id, TARGET_CHAT, path, cap, edit, topic_id)
        await edit.edit_text("Uploaded ✅")
    except Exception as e:
        await edit.edit_text(f"Failed: `{e}`")
