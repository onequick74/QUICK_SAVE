# devgagan/__main__.py
# ---------------------------------------------------
# STAR JAAT (fixed)

import asyncio
import importlib
import gc
import logging
from pyrogram import idle
from devgagan.modules import ALL_MODULES
from devgagan.core.mongo.plans_db import check_and_remove_expired_users
from aiojobs import create_scheduler

# ---------------------------------------------------
# Bot Start
# ---------------------------------------------------

loop = asyncio.get_event_loop()


async def schedule_expiry_check():
    """Periodically check & remove expired users from DB."""
    scheduler = create_scheduler()
    while True:
        try:
            await scheduler.spawn(check_and_remove_expired_users())
        except Exception as e:
            logging.error(f"Expiry check failed: {e}")
        # 1 hour interval
        await asyncio.sleep(3600)
        gc.collect()


async def devggn_boot():
    # Dynamically import all modules
    for module_name in ALL_MODULES:
        try:
            importlib.import_module("devgagan.modules." + module_name)
        except Exception as e:
            logging.error(f"Failed to load module {module_name}: {e}")

    print(
        """
---------------------------------------------------
📂 Bot Deployed successfully ...
📝 Description: A Pyrogram bot for downloading files from Telegram channels or groups 
                and uploading them back to Telegram.
👨‍💻 Author: Gagan
🌐 GitHub: https://github.com/calingrok/
📬 Telegram: https://t.me/jaat_one
▶️ YouTube: https://youtube.com/@calingrok
🗓️ Created: 2025-01-11
🔄 Last Modified: 2025-01-11
🛠️ Version: 2.0.5
📜 License: MIT License
---------------------------------------------------
"""
    )

    # Start background expiry check
    asyncio.create_task(schedule_expiry_check())
    print("Auto removal of expired users started ...")

    await idle()
    print("Bot stopped...")


if __name__ == "__main__":
    try:
        loop.run_until_complete(devggn_boot())
    except KeyboardInterrupt:
        print("Bot interrupted and shutting down...")
