from pyrogram import filters
from jaat import app
from jaat.core.mongo.plans_db import add_user_plan, remove_user_plan, get_user_plan, premium_users
from config import OWNER_ID

@app.on_message(filters.command("addplan") & filters.user(OWNER_ID))
async def add_plan(_, message):
    if len(message.command) < 3:
        return await message.reply_text("❌ Usage:\n`/addplan <user_id> <days>`")

    try:
        user_id = int(message.command[1])
        days = int(message.command[2])
    except ValueError:
        return await message.reply_text("⚠️ User ID aur days integer hone chahiye.")

    await add_user_plan(user_id, "premium", days)
    await message.reply_text(f"✅ Added premium plan for `{user_id}` for `{days}` days.")

@app.on_message(filters.command("removeplan") & filters.user(OWNER_ID))
async def remove_plan(_, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage:\n`/removeplan <user_id>`")

    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("⚠️ User ID galat hai.")

    await remove_user_plan(user_id)
    await message.reply_text(f"❌ Removed premium plan for `{user_id}`.")

@app.on_message(filters.command("myplan"))
async def my_plan(_, message):
    user_id = message.from_user.id
    plan = await get_user_plan(user_id)
    if not plan:
        return await message.reply_text("ℹ️ Aapke paas koi active plan nahi hai.")
    
    expiry = plan.get("expiry_date")
    await message.reply_text(f"💎 Aapka plan: `{plan['plan']}`\n📅 Expiry: `{expiry}`")

@app.on_message(filters.command("premiumusers") & filters.user(OWNER_ID))
async def list_premium(_, message):
    users = await premium_users()
    if not users:
        return await message.reply_text("😢 Koi premium user nahi mila.")
    txt = "💎 Premium Users:\n\n" + "\n".join([f"`{u}`" for u in users])
    await message.reply_text(txt)
