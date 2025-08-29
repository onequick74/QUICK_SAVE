from pyrogram import filters
from devgagan import app
from devgagan.core.mongo.users_db import get_users


# ----------------------------------------
# /id command - user ya chat ka ID batata hai
# ----------------------------------------
@app.on_message(filters.command("id") & filters.private)
async def show_id(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await message.reply_text(
        f"**Your Chat ID:** `{chat_id}`\n"
        f"**Your User ID:** `{user_id}`"
    )


# ----------------------------------------
# /get command - sab users ke IDs nikalne ke liye
# ----------------------------------------
@app.on_message(filters.command("get") & filters.user)
async def get_all_users(_, message):
    users = await get_users()
    if not users:
        return await message.reply_text("❌ No users found in database.")

    text = "**All User IDs:**\n\n"
    text += "\n".join([f"`{u}`" for u in users])

    # agar list bahut badi ho to file bhej de
    if len(text) > 4000:
        with open("users.txt", "w") as f:
            f.write("\n".join([str(u) for u in users]))
        await message.reply_document("users.txt")
    else:
        await message.reply_text(text)
