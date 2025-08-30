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
        await asyncio.sleep(3600)  # check every 1 hour
        gc.collect()

async def jaat_boot():
    for module_name in ALL_MODULES:
        try:
            importlib.import_module(f"jaat.modules.{module_name}")
        except Exception as e:
            print(f"[WARN] Failed to import module {module_name}: {e}")

    print("✅ Bot deployed successfully.")
    asyncio.create_task(schedule_expiry_check())
    print("⏳ Auto removal started ...")
    await idle()
    print("❌ Bot stopped.")

if __name__ == "__main__":
    loop.run_until_complete(jaat_boot())
