import asyncio
import traceback
from pyrogram import filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from config import OWNER_ID
from jaat import app
from jaat.core.mongo.users_db import get_users

async def send_msg(user_id, message):
    try:
        x = await message.copy(chat_id=user_id)
        try:
            await x.pin()
        except Exception:
            pass
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_msg(user_id, message)
    except InputUserDeactivated:
        return 400
    except UserIsBlocked:
        return 400
    except PeerIdInvalid:
        return 400
    except Exception:
        return 500
    return 200

@app.on_message(filters.command("gcast") & filters.user(OWNER_ID))
async def broadcast(_, message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to broadcast it.")

    exmsg = await message.reply_text("Broadcast started...")
    all_users = await get_users()
    done_users, failed_users = 0, 0
    
    for user in all_users:
        status = await send_msg(user, message.reply_to_message)
        if status == 200:
            done_users += 1
        else:
            failed_users += 1
        await asyncio.sleep(0.1)

    await exmsg.edit_text(
        f"✅ Broadcast finished.\n\n"
        f"📨 Sent: `{done_users}` users\n"
        f"❌ Failed: `{failed_users}` users"
    )

@app.on_message(filters.command("acast") & filters.user(OWNER_ID))
async def announced(_, message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a post to announce it.")

    exmsg = await message.reply_text("Announcement started...")
    users = await get_users()
    done_users, failed_users = 0, 0

    for user in users:
        try:
            await _.forward_messages(
                chat_id=int(user),
                from_chat_id=message.chat.id,
                message_ids=message.reply_to_message.id
            )
            done_users += 1
            await asyncio.sleep(0.5)
        except Exception:
            failed_users += 1

    await exmsg.edit_text(
        f"✅ Announcement finished.\n\n"
        f"📨 Sent: `{done_users}` users\n"
        f"❌ Failed: `{failed_users}` users"
      )
