import asyncio
from pyrogram import filters
from pytgcalls import PyTgCalls
from pytgcalls.types import StreamAudioEnded, StreamVideoEnded

from anony import app, pytgcalls

# ================= STORAGE =================
VC_LOG = {}  # chat_id: True / False


# ================= COMMAND =================
@app.on_message(filters.command("vclog") & filters.group)
async def vc_log_toggle(_, m):
    if len(m.command) < 2:
        return await m.reply_text(
            "❌ Usage:\n\n/vclog on\n/vclog off"
        )

    chat_id = m.chat.id
    opt = m.command[1].lower()

    if opt == "on":
        VC_LOG[chat_id] = True
        await m.reply_text("✅ VC Logger ENABLED")

    elif opt == "off":
        VC_LOG[chat_id] = False
        await m.reply_text("❌ VC Logger DISABLED")

    else:
        await m.reply_text("❌ Invalid option")


# ================= VC START =================
@pytgcalls.on_stream_start()
async def vc_started(_, chat_id):
    if not VC_LOG.get(chat_id):
        return

    msg = await app.send_message(
        chat_id,
        "<b>🎧 Voice Chat Started</b>",
        parse_mode="html"
    )
    await asyncio.sleep(5)
    await msg.delete()


# ================= VC END =================
@pytgcalls.on_stream_end()
async def vc_ended(_, chat_id):
    if not VC_LOG.get(chat_id):
        return

    msg = await app.send_message(
        chat_id,
        "<b>🔕 Voice Chat Ended</b>",
        parse_mode="html"
    )
    await asyncio.sleep(5)
    await msg.delete()
