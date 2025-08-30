import math
import time
import re
import cv2
import os
import asyncio
import subprocess
from datetime import datetime as dt
from pyrogram import enums
from config import CHANNEL_ID, OWNER_ID 
from jaat.core.mongo.plans_db import premium_users
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, InviteHashInvalid, InviteHashExpired, UserAlreadyParticipant, UserNotParticipant

async def chk_user(message, user_id):
    user = await premium_users()
    if user_id in user or user_id in OWNER_ID:
        return 0
    return 1

async def gen_link(app, chat_id):
    return await app.export_chat_invite_link(chat_id)

async def subscribe(app, message):
    update_channel = CHANNEL_ID
    url = await gen_link(app, update_channel)
    if update_channel:
        try:
            user = await app.get_chat_member(update_channel, message.from_user.id)
            if user.status == "kicked":
                await message.reply_text("You are Banned. Contact @jaat_support")
                return 1
        except UserNotParticipant:
            caption = "Join our channel to use the bot"
            await message.reply_photo(
                photo="https://graph.org/file/d44f024a08ded19452152.jpg",
                caption=caption,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Now...", url=f"{url}")]])
            )
            return 1
        except Exception:
            await message.reply_text("Something went wrong. Contact @jaat_support")
            return 1

async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value, index = "", 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1
        unit = ts[index:].lstrip()
        return int(value) if value else 0, unit

    value, unit = extract_value_and_unit(time_string)
    if unit == 's':
        return value
    elif unit == 'min':
        return value * 60
    elif unit == 'hour':
        return value * 3600
    elif unit == 'day':
        return value * 86400
    elif unit == 'month':
        return value * 2592000
    elif unit == 'year':
        return value * 31536000
    return 0

PROGRESS_BAR = """\n
│ **Completed:** {1}/{2}
│ **Progress:** {0}%
│ **Speed:** {3}/s
│ **ETA:** {4}
╰─────────────────────╯
"""

async def progress_bar(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.0) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["♦" for _ in range(math.floor(percentage / 10))]),
            ''.join(["◇" for _ in range(10 - math.floor(percentage / 10))])
        )

        tmp = progress + PROGRESS_BAR.format(
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(text="{}\n│ {}".format(ud_type, tmp))
        except:
            pass

def humanbytes(size):
    if not size:
        return ""
    power, n = 2**10, 0
    Dic_powerN = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s, ") if seconds else "") + \
          ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2] 

def convert(seconds):
    seconds %= (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

async def userbot_join(userbot, invite_link):
    try:
        await userbot.join_chat(invite_link)
        return "Successfully joined the Channel"
    except UserAlreadyParticipant:
        return "User is already a participant."
    except (InviteHashInvalid, InviteHashExpired):
        return "Invalid or expired invite link."
    except FloodWait:
        return "Too many requests, try again later."
    except Exception as e:
        print(e)
        return "Could not join, try manually."

def get_link(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)   
    try:
        link = [x[0] for x in url][0]
        return link if link else False
    except Exception:
        return False

def video_metadata(file):
    default_values = {'width': 1, 'height': 1, 'duration': 1}
    try:
        vcap = cv2.VideoCapture(file)
        if not vcap.isOpened():
            return default_values  
        width = round(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = round(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = vcap.get(cv2.CAP_PROP_FPS)
        frame_count = vcap.get(cv2.CAP_PROP_FRAME_COUNT)
        if fps <= 0:
            return default_values  
        duration = round(frame_count / fps)
        if duration <= 0:
            return default_values  
        vcap.release()
        return {'width': width, 'height': height, 'duration': duration}
    except Exception as e:
        print(f"Error in video_metadata: {e}")
        return default_values

def hhmmss(seconds):
    return time.strftime('%H:%M:%S', time.gmtime(seconds))

async def screenshot(video, duration, sender):
    if os.path.exists(f'{sender}.jpg'):
        return f'{sender}.jpg'
    time_stamp = hhmmss(int(duration)/2)
    out = dt.now().isoformat("_", "seconds") + ".jpg"
    cmd = ["ffmpeg", "-ss", f"{time_stamp}", "-i", f"{video}", "-frames:v", "1", f"{out}", "-y"]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    if os.path.isfile(out):
        return out
    return None  

last_update_time = time.time()

async def progress_callback(current, total, progress_message):
    percent = (current / total) * 100
    global last_update_time
    current_time = time.time()
    if current_time - last_update_time >= 10 or percent % 10 == 0:
        completed_blocks = int(percent // 10)
        remaining_blocks = 10 - completed_blocks
        bar = "♦" * completed_blocks + "◇" * remaining_blocks
        current_mb = current / (1024 * 1024)  
        total_mb = total / (1024 * 1024)      
        await progress_message.edit(
            f"╭──────────────────╮\n"
            f"│ Uploading...      \n"
            f"├──────────\n"
            f"│ {bar}\n\n"
            f"│ Progress: {percent:.2f}%\n"
            f"│ Uploaded: {current_mb:.2f} MB / {total_mb:.2f} MB\n"
            f"╰──────────────────╯\n\n"
            f"Powered by Star Jaat"
        )
        last_update_time = current_time
