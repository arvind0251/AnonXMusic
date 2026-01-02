# vc_logger.py
# Copyright (c) 2026 Rudra
# Licensed under the MIT License
# This file is part of AnonXMusic VC Logger

import asyncio
from pyrogram import filters, types
from anony import app  # Make sure 'app' is your Pyrogram Client

# ================= VC JOIN =================
@app.on_message(filters.new_chat_members & ~filters.bot)
async def vc_join_logger(_, m: types.Message):
    """
    Handles new members joining the group/VC
    """
    for user in m.new_chat_members:
        text = f"""
<b>#JoinVideoChat</b>

● ɴᴀᴍᴇ ➛ {user.first_name}
● ɪᴅ ➛ {user.id}
● ᴜsᴇʀɴᴀᴍᴇ ➛ @{user.username if user.username else 'N/A'}
"""
        msg = await m.reply_text(text, parse_mode="html")
        await asyncio.sleep(5)  # Auto-delete after 5 seconds
        await msg.delete()

# ================= VC LEAVE =================
@app.on_message(filters.left_chat_member & ~filters.bot)
async def vc_leave_logger(_, m: types.Message):
    """
    Handles members leaving the group/VC
    """
    user = m.left_chat_member
    text = f"""
<b>#LeaveVideoChat</b>

● ɴᴀᴍᴇ ➛ {user.first_name}
● ɪᴅ ➛ {user.id}
● ᴜsᴇʀɴᴀᴍᴇ ➛ @{user.username if user.username else 'N/A'}
"""
    msg = await m.reply_text(text, parse_mode="html")
    await asyncio.sleep(5)  # Auto-delete after 5 seconds
    await msg.delete()
