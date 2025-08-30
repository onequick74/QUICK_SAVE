import asyncio
import time
import gc
import os
import re
from typing import Optional
from jaat import app
from telethon.tl.types import DocumentAttributeVideo
import pymongo
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid
from pyrogram.enums import MessageMediaType, ParseMode
from jaat.core.funk import *   # ✅ fixed
from config import MONGO_DB, LOG_GROUP, OWNER_ID, STRING, API_ID, API_HASH
from jaat.core.mongo import db as odb

DB_NAME = "smart_users"
COLLECTION_NAME = "super_user"
mongo_app = pymongo.MongoClient(MONGO_DB)
db = mongo_app[DB_NAME]
collection = db[COLLECTION_NAME]

VIDEO_EXTENSIONS = {'mp4', 'mkv', 'avi', 'mov'}
IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}
DOCUMENT_EXTENSIONS = {'pdf', 'docx', 'txt', 'epub'}


def thumbnail(sender: str) -> Optional[str]:
    path = f"{sender}.jpg"
    return path if os.path.exists(path) else None


async def fetch_upload_method(user_id: int) -> str:
    user_data = collection.find_one({"user_id": user_id})
    return user_data.get("upload_method", "Pyrogram") if user_data else "Pyrogram"


async def format_caption_to_html(caption: str) -> str:
    if not caption:
        return None
    caption = re.sub(r"^> (.*)", r"<blockquote>\1</blockquote>", caption, flags=re.MULTILINE)
    caption = re.sub(r"```(.*?)```", r"<pre>\1</pre>", caption, flags=re.DOTALL)
    caption = re.sub(r"`(.*?)`", r"<code>\1</code>", caption)
    caption = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", caption)
    caption = re.sub(r"\*(.*?)\*", r"<b>\1</b>", caption)
    caption = re.sub(r"__(.*?)__", r"<i>\1</i>", caption)
    caption = re.sub(r"_(.*?)_", r"<i>\1</i>", caption)
    caption = re.sub(r"~~(.*?)~~", r"<s>\1</s>", caption)
    caption = re.sub(r"\|\|(.*?)\|\|", r"<details>\1</details>", caption)
    caption = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', caption)
    return caption.strip()


async def upload_media(sender, target_chat_id, file_path, caption, edit_message, topic_id):
    try:
        upload_method = await fetch_upload_method(sender)
        metadata = video_metadata(file_path)
        width, height, duration = metadata['width'], metadata['height'], metadata['duration']

        thumb = None
        try:
            thumb = await screenshot(file_path, duration, sender)
        except Exception:
            thumb = None

        ext = file_path.split('.')[-1].lower()

        if upload_method == "Pyrogram":
            if ext in VIDEO_EXTENSIONS:
                sent = await app.send_video(
                    chat_id=target_chat_id,
                    video=file_path,
                    caption=caption,
                    height=height,
                    width=width,
                    duration=duration,
                    thumb=thumb,
                    reply_to_message_id=topic_id,
                    parse_mode=ParseMode.MARKDOWN,
                    progress=progress_bar,
                    progress_args=("Uploading:", edit_message, time.time())
                )
            elif ext in IMAGE_EXTENSIONS:
                sent = await app.send_photo(
                    chat_id=target_chat_id,
                    photo=file_path,
                    caption=caption,
                    reply_to_message_id=topic_id,
                    parse_mode=ParseMode.MARKDOWN,
                    progress=progress_bar,
                    progress_args=("Uploading:", edit_message, time.time())
                )
            else:
                sent = await app.send_document(
                    chat_id=target_chat_id,
                    document=file_path,
                    caption=caption,
                    thumb=thumb,
                    reply_to_message_id=topic_id,
                    parse_mode=ParseMode.MARKDOWN,
                    progress=progress_bar,
                    progress_args=("Uploading:", edit_message, time.time())
                )
            try:
                await sent.copy(LOG_GROUP)
            except Exception:
                pass

    except Exception as e:
        try:
            await app.send_message(LOG_GROUP, f"**Upload Failed:** {str(e)}")
        except Exception:
            pass
        print("Upload error:", e)

    finally:
        if thumb and os.path.exists(thumb):
            try:
                os.remove(thumb)
            except Exception:
                pass
        gc.collect()
