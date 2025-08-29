from pyrogram import Client, filters

@Client.on_message(filters.command("id") & filters.group)
async def get_group_id(client, message):
    await message.reply_text(f"Group/Channel ID: `{message.chat.id}`")

@Client.on_message(filters.command("id") & filters.private)
async def get_private_id(client, message):
    await message.reply_text(f"Your User ID: `{message.from_user.id}`")
