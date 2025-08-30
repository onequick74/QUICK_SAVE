from jaat import app  # ✅ folder name updated
from pyrogram import idle
import asyncio


async def main():
    print("🚀 Star Jaat Bot starting ...")
    await app.start()
    print("✅ Bot started successfully! Waiting for events ...")
    await idle()
    await app.stop()
    print("🛑 Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
