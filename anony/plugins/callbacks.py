# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

import re
from pyrogram import filters, types

from anony import anon, app, db, lang, queue, tg, yt
from anony.helpers import admin_check, buttons, can_manage_vc


# ================= CANCEL DOWNLOAD =================
@app.on_callback_query(filters.regex("^cancel_dl$") & ~app.bl_users)
@lang.language()
async def cancel_dl(_, query: types.CallbackQuery):
    await query.answer()
    await tg.cancel(query)


# ================= PLAYER CONTROLS =================
@app.on_callback_query(filters.regex("^controls") & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _controls(_, query: types.CallbackQuery):
    args = query.data.split()
    action, chat_id = args[1], int(args[2])
    user = query.from_user.mention

    if not await db.get_call(chat_id):
        return await query.answer(query.lang["not_playing"], show_alert=True)

    if action == "status":
        return await query.answer()

    await query.answer(query.lang["processing"], show_alert=True)

    if action == "pause":
        if not await db.playing(chat_id):
            return await query.answer(
                query.lang["play_already_paused"], show_alert=True
            )
        await anon.pause(chat_id)
        status = query.lang["paused"]
        reply = query.lang["play_paused"].format(user)

    elif action == "resume":
        if await db.playing(chat_id):
            return await query.answer(
                query.lang["play_not_paused"], show_alert=True
            )
        await anon.resume(chat_id)
        status = query.lang["playing"]
        reply = query.lang["play_resumed"].format(user)

    elif action == "skip":
        await anon.play_next(chat_id)
        status = query.lang["skipped"]
        reply = query.lang["play_skipped"].format(user)

    elif action == "replay":
        media = queue.get_current(chat_id)
        media.user = user
        await anon.replay(chat_id)
        status = query.lang["replayed"]
        reply = query.lang["play_replayed"].format(user)

    elif action == "stop":
        await anon.stop(chat_id)
        status = query.lang["stopped"]
        reply = query.lang["play_stopped"].format(user)

    else:
        return

    try:
        if action in ["skip", "replay", "stop"]:
            await query.message.reply_text(reply, quote=False)
            await query.message.delete()
        else:
            text = query.message.text or query.message.caption or ""
            text = re.sub(r"\n\n.*$", "", text, flags=re.DOTALL)

            await query.edit_message_text(
                f"{text}\n\n{reply}",
                reply_markup=buttons.controls(chat_id, status=status),
            )
    except:
        pass


# ================= HELP MENU (FIXED & SAFE) =================
@app.on_callback_query(filters.regex("^help") & ~app.bl_users)
@lang.language()
async def _help(_, query: types.CallbackQuery):
    data = query.data.split()

    # help
    if len(data) == 1:
        return await query.edit_message_text(
            text=query.lang["help_menu"],
            reply_markup=buttons.help_markup(query.lang),
        )

    # help back
    if data[1] == "back":
        return await query.edit_message_text(
            text=query.lang["help_menu"],
            reply_markup=buttons.help_markup(query.lang),
        )

    # help close
    if data[1] == "close":
        try:
            await query.message.delete()
        except:
            pass
        return

    # help something (safe)
    key = f"help_{data[1]}"
    text = query.lang.get(key, query.lang["help_menu"])

    await query.edit_message_text(
        text=text,
        reply_markup=buttons.help_markup(query.lang, True),
    )


# ================= PLAY MODE =================
@app.on_callback_query(filters.regex("^playmode") & ~app.bl_users)
@lang.language()
@admin_check
async def _playmode(_, query: types.CallbackQuery):
    await query.answer(query.lang["processing"], show_alert=True)

    chat_id = query.message.chat.id
    admin_only = await db.get_play_mode(chat_id)
    _language = await db.get_lang(chat_id)

    await db.set_play_mode(chat_id, admin_only)

    await query.edit_message_reply_markup(
        reply_markup=buttons.settings_markup(
            query.lang,
            not admin_only,
            _language,
            chat_id,
        )
    )
