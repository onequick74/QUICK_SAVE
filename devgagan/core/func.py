import asyncio, os, subprocess, json, time, re, gc
from typing import Optional, Dict, Any
from pyrogram.enums import ParseMode

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
        if "streams" in data and data["streams"]:
            s = data["streams"][0]
            width = int(s.get("width", width))
            height = int(s.get("height", height))
        if "format" in data and "duration" in data["format"] and data["format"]["duration"]:
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
        ts = min(1, max(0, duration - duration))  # 1s or 0 if unknown
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
        text = f"**Uploading:** {pct:.2f}% • {current//(1024*1024)}MB/{total//(1024*1024)}MB\n" \
               f"**Speed:** {speed/1024/1024:.2f} MB/s"
        await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    except Exception:
        pass

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
    c = re.sub(r"^> (.*)", r"<blockquote>\1</blockquote>", c, flags=re.MULTILINE)
    c = re.sub(r"```(.*?)```", r"<pre>\1</pre>", c, flags=re.DOTALL)
    c = re.sub(r"`(.*?)`", r"<code>\1</code>", c)
    c = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", c)
    c = re.sub(r"\*(.*?)\*", r"<b>\1</b>", c)
    c = re.sub(r"__(.*?)__", r"<i>\1</i>", c)
    c = re.sub(r"_(.*?)_", r"<i>\1</i>", c)
    c = re.sub(r"~~(.*?)~~", r"<s>\1</s>", c)
    c = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', c)
    return c.strip()
