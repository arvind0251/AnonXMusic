# vc_logger.py
# Copyright (c) 2026 Rudra
# Licensed under the MIT License
# This plugin logs VC join/leave events with auto-delete messages

import asyncio
from pyrogram import filters, types
from pyrogram.types import ChatMemberUpdated
from anony import app

# ----------------- VC JOIN / LEAVE LOGGER -----------------
@app.on_chat_member_updated()
async def vc_join_leave(client: app, update: ChatMemberUpdated):
    old = update.old_chat_member
    new = update.new_chat_member
    user = update.from_user
    chat_id = update.chat.id

    # Ignore if user info not available
    if not user:
        return

    # USER JOINED VC
    if old.status in ["left", "kicked"] and new.status in ["member", "administrator"]:
        text = (
            f"● ɴᴀᴍᴇ ➛ {user.first_name}\n"
            f"● ɪᴅ ➛ {user.id}\n"
            f"● ᴜsᴇʀɴᴀᴍᴇ ➛ @{user.username}\n"
            f"Joined the VC!"
        )
        msg = await app.send_message(chat_id, text, parse_mode=types.ParseMode.HTML)
        await asyncio.sleep(5)
        await msg.delete()

    # USER LEFT VC
    elif old.status in ["member", "administrator"] and new.status in ["left", "kicked"]:
        text = (
            f"● ɴᴀᴍᴇ ➛ {user.first_name}\n"
            f"● ɪᴅ ➛ {user.id}\n"
            f"● ᴜsᴇʀɴᴀᴍᴇ ➛ @{user.username}\n"
            f"Left the VC!"
        )
        msg = await app.send_message(chat_id, text, parse_mode=types.ParseMode.HTML)
        await asyncio.sleep(5)
        await msg.delete()
