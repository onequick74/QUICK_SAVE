# devgagan/core/func.py

import os, subprocess, json, time, re
from typing import Optional, Dict, Any
from pyrogram.enums import ParseMode
from pyrogram.errors import MessageNotModified, MessageIdInvalid

# -------- Video metadata via ffprobe (fallback to defaults) ----------
def video_metadata(path: str) -> Dict[str, Any]:
    width, height, duration = 1280, 720, 0
    try:
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height:format=duration",
            "-of", "json", path
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
        data = json.loads(out)

        if data.get("streams"):
            s = data["streams"][0]
            width = int(s.get("width", width))
            height = int(s.get("height", height))

        if "format" in data and data["format"].get("duration"):
            duration = int(float(data["format"]["duration"]))

    except Exception:
        pass

    return {"width": width, "height": height, "duration": duration}


# -------- Thumb via ffmpeg (returns path or None) ----------
async def screenshot(path: str, duration: int, sender: int) -> Optional[str]:
    try:
        out_dir = "/tmp/thumbs"
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{sender}.jpg")

        # Pick a frame from mid-duration, else 1s fallback
        ts = 1
        if duration and duration > 2:
            ts = duration // 2

        cmd = ["ffmpeg", "-y", "-ss", str(ts), "-i", path, "-frames:v", "1", out_path]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)

        return out_path if os.path.exists(out_path) else None
    except Exception:
        return None


# -------- Generic progress callback for Pyrogram sends ----------
async def progress_bar(current, total, message, start):
    try:
        now = time.time()
        diff = max(1e-6, now - start)
        pct = current * 100 / max(1, total)
        speed = current / diff
        text = (
            f"**Uploading:** {pct:.2f}% "
            f"• {current//(1024*1024)}MB/{total//(1024*1024)}MB\n"
            f"**Speed:** {speed/1024/1024:.2f} MB/s"
        )
        await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    except (MessageNotModified, MessageIdInvalid):
        # Ignore safe edit errors
        pass
    except Exception as e:
        print(f"Progress update failed: {e}")


def progress_callback(done, total, tag=""):
    try:
        pct = int(done * 100 / max(1, total))
        print(f"[{tag}] {pct}%")
    except Exception:
        pass


# -------- Markdown → HTML (basic) ----------
def md_to_html(caption: Optional[str]) -> Optional[str]:
    if not caption:
        return None
    c = caption

    # code blocks first
    c = re.sub(r"```(.*?)```", r"<pre>\1</pre>", c, flags=re.DOTALL)
    c = re.sub(r"`(.*?)`", r"<code>\1</code>", c)

    # blockquotes
    c = re.sub(r"^> (.*)", r"<blockquote>\1</blockquote>", c, flags=re.MULTILINE)

    # styles
    c = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", c)
    c = re.sub(r"\*(.*?)\*", r"<b>\1</b>", c)
    c = re.sub(r"__(.*?)__", r"<i>\1</i>", c)
    c = re.sub(r"_(.*?)_", r"<i>\1</i>", c)
    c = re.sub(r"~~(.*?)~~", r"<s>\1</s>", c)

    # links
    c = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', c)

    return c.strip()
