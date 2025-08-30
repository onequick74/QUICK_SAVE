import asyncio
import time
import gc
import os
import re
from typing import Optional
from jaat import app
from jaat import sex as gf
from telethon.tl.types import DocumentAttributeVideo
import pymongo
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message as PyroMessage
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid, RPCError
from pyrogram.enums import MessageMediaType, ParseMode
from jaat.core.func import *
from config import MONGO_DB as MONGODB_CONNECTION_STRING, LOG_GROUP, OWNER_ID, STRING, API_ID, API_HASH
from jaat.core.mongo import db as odb

# Optional fast uploader (third-party). If unavailable, Telethon upload path will raise a clear error.
try:
    from devgagantools import fast_upload
except Exception:
    fast_upload = None

# MongoDB settings (used for per-user preferences in this module)
DB_NAME = "smart_users"
COLLECTION_NAME = "super_user"
mongo_app = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
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
            # copy to log group (if available)
            try:
                await sent.copy(LOG_GROUP)
            except Exception:
                pass

        elif upload_method == "Telethon":
            if fast_upload is None:
                raise RuntimeError("Telethon fast_upload is not available on this environment.")
            # Use telethon client to upload
            await edit_message.delete()
            progress_message = await gf.send_message(sender, "**Uploading...**")
            html_caption = await format_caption_to_html(caption) if caption else None
            uploaded = await fast_upload(
                gf, file_path,
                reply=progress_message,
                name=None,
                progress_bar_function=lambda d, t: asyncio.get_event_loop().create_task(progress_callback(d, t, progress_message))
            )
            await progress_message.delete()

            attributes = []
            if ext in VIDEO_EXTENSIONS:
                attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, supports_streaming=True)]

            await gf.send_file(
                target_chat_id,
                uploaded,
                caption=html_caption,
                attributes=attributes,
                reply_to=topic_id,
                thumb=thumb,
                parse_mode='html'
            )
            try:
                await gf.send_file(LOG_GROUP, uploaded, caption=html_caption, attributes=attributes, thumb=thumb, parse_mode='html')
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

async def get_msg(userbot, sender, edit_id, msg_link, i, message_obj):
    """
    Main entry to fetch a message from a link (userbot/telethon) and deliver/upload it to target chat.
    """
    edit = None
    file_path = None
    try:
        msg_link = msg_link.split("?single")[0].strip()
        saved_channel_ids = load_saved_channel_ids()  # assumed in core.func
        size_limit = 2 * 1024 * 1024 * 1024  # ~2GB

        # parse link types
        if 't.me/c/' in msg_link or 't.me/b/' in msg_link:
            parts = msg_link.rstrip('/').split('/')
            if 't.me/b/' in msg_link:
                # sometimes these are like t.me/b/username/msgid
                chat = parts[-2]
                msg_id = int(parts[-1]) + i
            else:
                # t.me/c/{chat_id}/{msg_id}
                try:
                    idx = parts.index('c')
                    chat = int('-100' + parts[idx + 1])
                except Exception:
                    # fallback: attempt to extract numeric part near 'c'
                    chat = None
                msg_id = int(parts[-1]) + i

            if chat in saved_channel_ids:
                await app.edit_message_text(message_obj.chat.id, edit_id, "Sorry! This channel is protected.")
                return

        elif '/s/' in msg_link:
            edit = await app.edit_message_text(sender, edit_id, "Story link detected...")
            if userbot is None:
                await edit.edit("Login required to fetch stories.")
                return
            parts = msg_link.rstrip('/').split('/')
            chat = parts[3]
            if chat.isdigit():
                chat = f"-100{chat}"
            msg_id = int(parts[-1])
            await download_user_stories(userbot, chat, msg_id, edit, sender)
            await edit.delete()
            return

        else:
            edit = await app.edit_message_text(sender, edit_id, "Public link detected...")
            chat = msg_link.split("t.me/")[1].split("/")[0]
            msg_id = int(msg_link.rstrip('/').split("/")[-1])
            await copy_message_with_chat_id(app, userbot, sender, chat, msg_id, edit)
            await edit.delete()
            return

        # fetch message using userbot (telethon or pyrogram session)
        msg = await userbot.get_messages(chat, msg_id)
        if not msg or getattr(msg, "service", False) or getattr(msg, "empty", False):
            await app.delete_messages(sender, edit_id)
            return

        target_chat_id = user_chat_ids.get(message_obj.chat.id, message_obj.chat.id)
        topic_id = None
        if '/' in str(target_chat_id):
            # e.g. "-100123456789/2"
            parts = str(target_chat_id).split('/', 1)
            target_chat_id = int(parts[0])
            topic_id = int(parts[1])

        # handle quick types
        if getattr(msg, "media", None) == MessageMediaType.WEB_PAGE_PREVIEW:
            await clone_message(app, msg, target_chat_id, topic_id, edit_id, LOG_GROUP)
            return

        if getattr(msg, "text", None):
            await clone_text_message(app, msg, target_chat_id, topic_id, edit_id, LOG_GROUP)
            return

        if getattr(msg, "sticker", None):
            await handle_sticker(app, msg, target_chat_id, topic_id, edit_id, LOG_GROUP)
            return

        file_size = get_message_file_size(msg)
        file_name = await get_media_filename(msg)
        edit = await app.edit_message_text(sender, edit_id, "**Downloading...**")

        # Download media (via userbot)
        file_path = await userbot.download_media(
            msg,
            file_name=file_name,
            progress=progress_bar,
            progress_args=("Downloading:", edit, time.time())
        )

        caption = await get_final_caption(msg, sender)
        file_path = await rename_file(file_path, sender)

        # Quick send for small specific types
        if getattr(msg, "audio", None):
            result = await app.send_audio(target_chat_id, file_path, caption=caption, reply_to_message_id=topic_id)
            await result.copy(LOG_GROUP)
            await edit.delete()
            os.remove(file_path)
            return

        if getattr(msg, "voice", None):
            result = await app.send_voice(target_chat_id, file_path, reply_to_message_id=topic_id)
            await result.copy(LOG_GROUP)
            await edit.delete()
            os.remove(file_path)
            return

        if getattr(msg, "video_note", None):
            result = await app.send_video_note(target_chat_id, file_path, reply_to_message_id=topic_id)
            await result.copy(LOG_GROUP)
            await edit.delete()
            os.remove(file_path)
            return

        if getattr(msg, "photo", None):
            result = await app.send_photo(target_chat_id, file_path, caption=caption, reply_to_message_id=topic_id)
            await result.copy(LOG_GROUP)
            await edit.delete()
            os.remove(file_path)
            return

        # If file too large, handle split/upload logic or fallback
        if file_size and file_size > size_limit and (free_check == 1 or pro is None):
            await edit.delete()
            await split_and_upload_file(app, sender, target_chat_id, file_path, caption, topic_id)
            return
        elif file_size and file_size > size_limit:
            await handle_large_file(file_path, sender, edit, caption)
            return
        else:
            await upload_media(sender, target_chat_id, file_path, caption, edit, topic_id)

    except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid):
        try:
            await app.edit_message_text(sender, edit_id, "Have you joined the channel?")
        except Exception:
            pass
    except Exception as e:
        print("get_msg error:", e)
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        if edit:
            try:
                await edit.delete()
            except Exception:
                pass
        gc.collect()

# helper clones / small utilities

async def clone_message(app_client, msg, target_chat_id, topic_id, edit_id, log_group):
    edit = await app_client.edit_message_text(target_chat_id, edit_id, "Cloning...")
    try:
        txt = msg.text.markdown if msg.text else ""
        sent = await app_client.send_message(target_chat_id, txt, reply_to_message_id=topic_id)
        await sent.copy(log_group)
    except Exception as e:
        print("clone_message error:", e)
    finally:
        await edit.delete()

async def clone_text_message(app_client, msg, target_chat_id, topic_id, edit_id, log_group):
    edit = await app_client.edit_message_text(target_chat_id, edit_id, "Cloning text...")
    try:
        txt = msg.text.markdown if msg.text else ""
        sent = await app_client.send_message(target_chat_id, txt, reply_to_message_id=topic_id)
        await sent.copy(log_group)
    except Exception as e:
        print("clone_text_message error:", e)
    finally:
        await edit.delete()

async def handle_sticker(app_client, msg, target_chat_id, topic_id, edit_id, log_group):
    edit = await app_client.edit_message_text(target_chat_id, edit_id, "Handling sticker...")
    try:
        result = await app_client.send_sticker(target_chat_id, msg.sticker.file_id, reply_to_message_id=topic_id)
        await result.copy(log_group)
    except Exception as e:
        print("handle_sticker error:", e)
    finally:
        await edit.delete()

async def get_media_filename(msg):
    if getattr(msg, "document", None):
        return msg.document.file_name
    if getattr(msg, "video", None):
        return getattr(msg.video, "file_name", "temp.mp4")
    if getattr(msg, "photo", None):
        return "temp.jpg"
    return "unknown_file"

def get_message_file_size(msg):
    if getattr(msg, "document", None):
        return msg.document.file_size
    if getattr(msg, "photo", None):
        return msg.photo.file_size
    if getattr(msg, "video", None):
        return msg.video.file_size
    return 0

async def get_final_caption(msg, sender):
    original = msg.caption.markdown if getattr(msg, "caption", None) else ""
    custom = get_user_caption_preference(sender)
    final = f"{original}\n\n{custom}" if custom else original
    replacements = load_replacement_words(sender)
    for k, v in (replacements or {}).items():
        final = final.replace(k, v)
    return final if final else None

async def download_user_stories(userbot, chat_id, msg_id, edit, sender):
    try:
        story = await userbot.get_stories(chat_id, msg_id)
        if not story:
            await edit.edit("No story available.")
            return
        if not getattr(story, "media", None):
            await edit.edit("Story has no media.")
            return
        await edit.edit("Downloading story...")
        file_path = await userbot.download_media(story)
        if getattr(story, "media", None) == MessageMediaType.VIDEO:
            await app.send_video(sender, file_path)
        elif getattr(story, "media", None) == MessageMediaType.DOCUMENT:
            await app.send_document(sender, file_path)
        elif getattr(story, "media", None) == MessageMediaType.PHOTO:
            await app.send_photo(sender, file_path)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        await edit.edit("Done.")
    except Exception as e:
        print("download_user_stories error:", e)
        try:
            await edit.edit(f"Error: {e}")
        except Exception:
            pass
