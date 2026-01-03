import asyncio
from pyrogram import filters
from pytgcalls.types import Update
from pytgcalls.types.call_participant import CallParticipant

from anony import app, pytgcalls

# ================= STORAGE =================
VC_LOG_STATUS = {}  # chat_id: True/False


# ================= COMMAND =================
@app.on_message(filters.command("vclog") & filters.group)
async def vc_log_toggle(_, m):
    if len(m.command) < 2:
        return await m.reply_text(
            "❌ Usage:\n\n/vclog on\n/vclog off"
        )

    chat_id = m.chat.id
    option = m.command[1].lower()

    if option == "on":
        VC_LOG_STATUS[chat_id] = True
        await m.reply_text("✅ VC Join/Leave Logger **ENABLED**")

    elif option == "off":
        VC_LOG_STATUS[chat_id] = False
        await m.reply_text("❌ VC Join/Leave Logger **DISABLED**")

    else:
        await m.reply_text("❌ Invalid option\nUse: on / off")


# ================= VC EVENTS =================
@pytgcalls.on_update()
async def vc_join_leave(_, update: Update):

    if not isinstance(update, CallParticipant):
        return

    chat_id = update.chat_id

    # Logger OFF hai
    if not VC_LOG_STATUS.get(chat_id):
        return

    user = update.user
    if not user:
        return

    username = f"@{user.username}" if user.username else "N/A"

    # ================= JOIN =================
    if update.joined:
        text = (
            "<b>#JoinVideoChat</b>\n\n"
            f"● ɴᴀᴍᴇ ➛ {user.first_name}\n"
            f"● ɪᴅ ➛ <code>{user.id}</code>\n"
            f"● ᴜsᴇʀɴᴀᴍᴇ ➛ {username}"
        )

        msg = await app.send_message(chat_id, text, parse_mode="html")
        await asyncio.sleep(5)
        await msg.delete()

    # ================= LEAVE =================
    if update.left:
        text = (
            "<b>#LeaveVideoChat</b>\n\n"
            f"● ɴᴀᴍᴇ ➛ {user.first_name}\n"
            f"● ɪᴅ ➛ <code>{user.id}</code>\n"
            f"● ᴜsᴇʀɴᴀᴍᴇ ➛ {username}"
        )

        msg = await app.send_message(chat_id, text, parse_mode="html")
        await asyncio.sleep(5)
        await msg.delete()
