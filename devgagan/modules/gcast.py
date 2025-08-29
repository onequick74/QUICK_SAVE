# STAR JAAT
# ---------------------------------------------------

import asyncio
import traceback
from pyrogram import filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid

from config import OWNER_ID
from devgagan import app
from devgagan.core.mongo.users_db import get_users


async def send_msg(user_id, message):
    try:
        x = await message.copy(chat_id=user_id)
        try:
            await x.pin()
        except Exception:
            await x.pin(both_sides=True)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


# Global Broadcast
@app.on_message(filters.command("gcast") & filters.user(OWNER_ID))
async def broadcast(_, message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to broadcast it.")
        return    

    exmsg = await message.reply_text("Started broadcasting...")
    all_users = (await get_users()) or {}
    done_users = 0
    failed_users = 0
    
    for user in all_users:
        try:
            await send_msg(user, message.reply_to_message)
            done_users += 1
            await asyncio.sleep(0.1)
        except Exception:
            failed_users += 1

    await exmsg.edit_text(
        f"✅ Broadcast Finished\n\n"
        f"✔ Sent: `{done_users}` users\n"
        f"❌ Failed: `{failed_users}` users"
    )


# Announcement Broadcast
@app.on_message(filters.command("acast") & filters.user(OWNER_ID))
async def announced(_, message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to broadcast")

    exmsg = await message.reply_text("Started announcement broadcast...")
    users = await get_users() or []
    done_users = 0
    failed_users = 0
  
    for user in users:
        try:
            await _.forward_messages(
                chat_id=int(user),
                from_chat_id=message.chat.id,
                message_ids=message.reply_to_message.id
            )
            done_users += 1
            await asyncio.sleep(1)
        except Exception:
            failed_users += 1
          
    await exmsg.edit_text(
        f"✅ Announcement Finished\n\n"
        f"✔ Sent: `{done_users}` users\n"
        f"❌ Failed: `{failed_users}` users"
    )
