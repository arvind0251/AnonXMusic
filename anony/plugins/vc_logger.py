from pyrogram import filters
from anony import app
from pyrogram.types import ChatMemberUpdated

@app.on_chat_member_updated()
async def vc_join_leave(client, update: ChatMemberUpdated):
    old = update.old_chat_member
    new = update.new_chat_member
    user = update.from_user

    if old.status in ["left", "kicked"] and new.status in ["member", "administrator"]:
        msg = f"● ɴᴀᴍᴇ ➛ {user.first_name}\n● ɪᴅ ➛ {user.id}\n● ᴜsᴇʀɴᴀᴍᴇ ➛ @{user.username}\nJoined the VC!"
        m = await app.send_message(update.chat.id, msg)
        await asyncio.sleep(5)
        await m.delete()

    elif old.status in ["member", "administrator"] and new.status in ["left", "kicked"]:
        msg = f"● ɴᴀᴍᴇ ➛ {user.first_name}\n● ɪᴅ ➛ {user.id}\n● ᴜsᴇʀɴᴀᴍᴇ ➛ @{user.username}\nLeft the VC!"
        m = await app.send_message(update.chat.id, msg)
        await asyncio.sleep(5)
        await m.delete()
