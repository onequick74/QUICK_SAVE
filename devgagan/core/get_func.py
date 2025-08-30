# devgagan/core/get_func.py

from pyrogram.types import Message

async def get_msg(message: Message) -> str:
    """
    Extract text or caption safely from a Pyrogram message.
    """
    if message.text:
        return message.text
    if message.caption:
        return message.caption
    return ""
