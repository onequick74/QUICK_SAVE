import asyncio
import importlib
import gc
from pyrogram import idle
from jaat.modules import ALL_MODULES
from jaat.core.mongo.plans_db import check_and_remove_expired_users
from aiojobs import create_scheduler

loop = asyncio.get_event_loop()

async def schedule_expiry_check():
    scheduler = await create_scheduler()
    while True:
        await scheduler.spawn(check_and_remove_expired_users())
        await asyncio.sleep(60)
        gc.collect()

async def devggn_boot():
    for all_module in ALL_MODULES:
        importlib.import_module("jaat.modules." + all_module)
    print("""
---------------------------------------------------
📂 Bot Deployed successfully ...
📝 Description: A Pyrogram bot for downloading files from Telegram channels or groups 
                and uploading them back to Telegram.
---------------------------------------------------
""")

    asyncio.create_task(schedule_expiry_check())
    print("Auto removal started ...")
    await idle()
    print("Bot stopped...")

if __name__ == "__main__":
    loop.run_until_complete(devggn_boot())
