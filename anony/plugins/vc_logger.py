from pyrogram import filters
from pyrogram.types import ChatMemberUpdated
from anony import app
import asyncio


@app.on_chat_member_updated(filters.group)
async def vc_join_leave(_, m: ChatMemberUpdated):
    old = m.old_chat_member
    new = m.new_chat_member

    # None safety check (VERY IMPORTANT)
    if not old or not new:
        return

    user = m.from_user
    if not user:
        return

    # USER JOIN
    if old.status in ("left", "kicked") and new.status in ("member", "administrator"):
        text = (
            "<b>#JoinGroup</b>\n\n"
            f"● ɴᴀᴍᴇ ➛ {user.first_name}\n"
            f"● ɪᴅ ➛ <code>{user.id}</code>\n"
            f"● ᴜsᴇʀɴᴀᴍᴇ ➛ @{user.username if user.username else 'N/A'}"
        )

        msg = await m.chat.send_message(text, parse_mode="html")
        await asyncio.sleep(5)
        await msg.delete()

    # USER LEAVE
    if old.status in ("member", "administrator") and new.status in ("left", "kicked"):
        text = (
            "<b>#LeaveGroup</b>\n\n"
            f"● ɴᴀᴍᴇ ➛ {user.first_name}\n"
            f"● ɪᴅ ➛ <code>{user.id}</code>\n"
            f"● ᴜsᴇʀɴᴀᴍᴇ ➛ @{user.username if user.username else 'N/A'}"
        )

        msg = await m.chat.send_message(text, parse_mode="html")
        await asyncio.sleep(5)
        await msg.delete()
