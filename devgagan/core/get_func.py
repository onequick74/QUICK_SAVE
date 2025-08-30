# devgagan/core/get_func.py

from pyrogram.types import Message

async def get_msg(message: Message) -> str:
    """
    Extract text or caption safely from a Pyrogram message.
    Priority:
    1. message.text
    2. message.caption
    3. replied message (text or caption)
    Returns empty string if nothing found.
    """
    if message.text:
        return message.text.strip()
    if message.caption:
        return message.caption.strip()

    # If no direct text/caption, try from replied message
    if message.reply_to_message:
        if message.reply_to_message.text:
            return message.reply_to_message.text.strip()
        if message.reply_to_message.caption:
            return message.reply_to_message.caption.strip()

    return ""
