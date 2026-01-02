import asyncio
from pyrogram import filters, types
from pyrogram.enums import ChatMemberStatus
from anony import app


@app.on_chat_member_updated(filters.group)
async def vc_join_leave(_, m: types.ChatMemberUpdated):

    old = m.old_chat_member
    new = m.new_chat_member

    # 🛑 Safety check (MOST IMPORTANT)
    if not old or not new:
        return

    user = new.user
    chat = m.chat

    # Ignore bots
    if user.is_bot:
        return

    text = None

    # ✅ JOIN
    if old.status in [
        ChatMemberStatus.LEFT,
        ChatMemberStatus.BANNED
    ] and new.status in [
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR
    ]:
        text = (
            "<b>#JoinVideoChat</b>\n\n"
            f"● <b>NAME ➛</b> {user.first_name}\n"
            f"● <b>ID ➛</b> <code>{user.id}</code>\n"
            f"● <b>USERNAME ➛</b> @{user.username or 'None'}"
        )

    # ❌ LEAVE
    elif old.status in [
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR
    ] and new.status in [
        ChatMemberStatus.LEFT,
        ChatMemberStatus.BANNED
    ]:
        text = (
            "<b>#LeaveVideoChat</b>\n\n"
            f"● <b>NAME ➛</b> {user.first_name}\n"
            f"● <b>ID ➛</b> <code>{user.id}</code>\n"
            f"● <b>USERNAME ➛</b> @{user.username or 'None'}"
        )

    if not text:
        return

    # ✅ Send message
    msg = await app.send_message(
        chat_id=chat.id,
        text=text,
        parse_mode=types.ParseMode.HTML
    )

    # 🕒 Auto delete after 5 sec
    await asyncio.sleep(5)
    await msg.delete()
