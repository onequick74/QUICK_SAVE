import speedtest
from pyrogram import filters
from jaat import app

@app.on_message(filters.command("speedtest"))
async def run_speedtest(_, message):
    await message.reply_text("⏳ Running speedtest... Please wait.")

    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download()
        upload_speed = st.upload()
        ping = st.results.ping

        result_text = (
            "📶 **Speedtest Results** 📶\n\n"
            f"⚡ Download: `{download_speed / 1024 / 1024:.2f} Mbps`\n"
            f"⚡ Upload: `{upload_speed / 1024 / 1024:.2f} Mbps`\n"
            f"📡 Ping: `{ping} ms`"
        )

        await message.reply_text(result_text)
    except Exception as e:
        await message.reply_text(f"⚠️ Speedtest failed: `{str(e)}`")
