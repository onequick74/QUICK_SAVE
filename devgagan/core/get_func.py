# STAR JAAT

import asyncio, time, os, gc, re, pymongo
from typing import Dict
from devgagan import app
from devgagan import sex as gf
from telethon.tl.types import DocumentAttributeVideo, Message as TeleMessage
from pyrogram.types import Message as PyroMessage
from pyrogram.enums import ParseMode
from devgagantools import fast_upload

from config import MONGO_DB, LOG_GROUP, STRING
from devgagan.core.func import video_metadata, screenshot, md_to_html, progress_bar, progress_callback

# ---------------- thumbs per-user ----------------
user_thumbnails: Dict[int, str] = {}  # {sender_id: thumb_path}

def thumbnail(sender_id: int):
    return user_thumbnails.get(sender_id)

# ---------------- Mongo ----------------
DB_NAME = "smart_users"
COLLECTION_NAME = "super_user"
mongo_app = pymongo.MongoClient(MONGO_DB)
db = mongo_app[DB_NAME]
collection = db[COLLECTION_NAME]

async def fetch_upload_method(user_id: int) -> str:
    data = collection.find_one({"user_id": user_id})
    return (data or {}).get("upload_method", "Pyrogram")

# ---------------- main uploader ----------------
async def upload_media(sender_id: int, target_chat_id: int, file: str, caption: str, edit_message, topic_id: int | None):
    try:
        method = await fetch_upload_method(sender_id)
        meta = video_metadata(file)
        width, height, duration = meta["width"], meta["height"], meta["duration"]

        # thumb (once per user)
        if sender_id not in user_thumbnails or not os.path.exists(user_thumbnails[sender_id]):
            try:
                tp = await screenshot(file, duration, sender_id)
                user_thumbnails[sender_id] = tp if tp else None
            except Exception:
                user_thumbnails[sender_id] = None

        thumb_path = user_thumbnails.get(sender_id)
        ext = os.path.splitext(file)[1].lower().lstrip(".")
        is_video = ext in {"mp4", "mkv", "avi", "mov"}
        is_image = ext in {"jpg", "jpeg", "png"}

        if method == "Pyrogram":
            if is_video:
                dm = await app.send_video(
                    chat_id=target_chat_id,
                    video=file,
                    caption=caption,
                    height=height, width=width, duration=duration,
                    thumb=thumb_path,
                    reply_to_message_id=topic_id,
                    parse_mode=ParseMode.MARKDOWN,
                    progress=progress_bar,
                    progress_args=(edit_message, time.time())
                )
                if LOG_GROUP:
                    await dm.copy(LOG_GROUP)
            elif is_image:
                dm = await app.send_photo(
                    chat_id=target_chat_id,
                    photo=file,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=topic_id,
                    progress=progress_bar,
                    progress_args=(edit_message, time.time())
                )
                if LOG_GROUP:
                    await dm.copy(LOG_GROUP)
            else:
                dm = await app.send_document(
                    chat_id=target_chat_id,
                    document=file,
                    caption=caption,
                    thumb=thumb_path,
                    reply_to_message_id=topic_id,
                    parse_mode=ParseMode.MARKDOWN,
                    progress=progress_bar,
                    progress_args=(edit_message, time.time())
                )
                if LOG_GROUP:
                    await dm.copy(LOG_GROUP)

        else:  # Telethon
            if edit_message:
                try:
                    await edit_message.delete()
                except Exception:
                    pass

            progress_message = await gf.send_message(sender_id, "**Uploading…**")
            uploaded = await fast_upload(
                gf, file,
                reply=progress_message,
                name=None,
                progress_bar_function=lambda d, t: progress_callback(d, t, f"user:{sender_id}")
            )
            try:
                await progress_message.delete()
            except Exception:
                pass

            attributes = []
            if is_video:
                attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, supports_streaming=True)]

            await gf.send_file(
                target_chat_id, uploaded,
                caption=md_to_html(caption),
                attributes=attributes,
                reply_to=topic_id,
                parse_mode='html',
                thumb=thumb_path
            )
            if LOG_GROUP:
                await gf.send_file(
                    LOG_GROUP, uploaded,
                    caption=md_to_html(caption),
                    attributes=attributes,
                    parse_mode='html',
                    thumb=thumb_path
                )

    except Exception as e:
        try:
            await app.send_message(LOG_GROUP, f"**Upload Failed:** `{e}`")
        except Exception:
            pass
        print(f"[upload_media] error: {e}")
    finally:
        gc.collect()

# -------------- get_msg (was missing earlier) ----------------
async def get_msg(message):
    try:
        if isinstance(message, PyroMessage):
            return message.text or message.caption
        if isinstance(message, TeleMessage):
            return getattr(message, "message", None) or getattr(message, "text", None)
        # Generic best effort
        return getattr(message, "text", None) or getattr(message, "caption", None)
    except Exception as e:
        print(f"get_msg error: {e}")
        return None
