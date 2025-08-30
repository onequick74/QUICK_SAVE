import psutil
import platform
from datetime import datetime
from pyrogram import filters
from jaat import app
from jaat.core.mongo.users_db import get_users

START_TIME = datetime.utcnow()

def get_readable_time(seconds: int) -> str:
    count = 0
    time_list = []
    time_suffix_list = ["s", "m", "h", "d"]

    while count < 4:
        count += 1
        if seconds == 0:
            break
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        seconds = int(result)
        time_list.append(f"{int(remainder)}{time_suffix_list[count-1]}")

    return " ".join(time_list[::-1])

@app.on_message(filters.command("sysstats"))
async def system_stats(_, message):
    current_time = datetime.utcnow()
    uptime = get_readable_time(int((current_time - START_TIME).total_seconds()))

    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    users = await get_users()

    stats_text = (
        "📊 **System Stats** 📊\n\n"
        f"⏱ Uptime: `{uptime}`\n"
        f"👥 Users in DB: `{len(users)}`\n\n"
        f"💻 CPU Usage: `{cpu_usage}%`\n"
        f"📈 RAM Usage: `{memory.percent}%`\n"
        f"💾 Disk Usage: `{disk.percent}%`\n"
        f"⚙️ System: `{platform.system()} {platform.release()}`"
    )

    await message.reply_text(stats_text)
