import aiohttp
from pyrogram import filters
from jaat import app

API_URL = "https://is.gd/create.php?format=simple&url={}"

@app.on_message(filters.command("shrink"))
async def shrink_url(_, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage:\n`/shrink <URL>`")

    url = message.text.split(" ", 1)[1]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL.format(url)) as resp:
                if resp.status == 200:
                    short_url = await resp.text()
                    return await message.reply_text(f"🔗 Shortened URL:\n{short_url}")
                else:
                    return await message.reply_text("⚠️ Failed to shorten the link.")
    except Exception as e:
        await message.reply_text(f"⚠️ Error: `{str(e)}`")
