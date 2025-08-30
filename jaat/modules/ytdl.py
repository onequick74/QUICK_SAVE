import os
import yt_dlp
from pyrogram import filters
from jaat import app

DOWNLOAD_DIR = "downloads"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def ytdl_opts(format="best"):
    return {
        "format": format,
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
    }

@app.on_message(filters.command("ytdl"))
async def ytdl_download(_, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage:\n`/ytdl <YouTube URL>`")

    url = message.text.split(" ", 1)[1]
    msg = await message.reply_text("⏳ Downloading... Please wait.")

    try:
        with yt_dlp.YoutubeDL(ytdl_opts("best")) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await message.reply_video(file_path, caption=f"✅ Downloaded: {info.get('title')}")
        await msg.delete()

        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await msg.edit(f"⚠️ Download failed: `{str(e)}`")
