# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

from pathlib import Path
from pyrogram import filters, types

from anony import anon, app, config, db, lang, queue, tg, yt
from anony.helpers import buttons, utils
from anony.helpers._play import checkUB


def playlist_to_queue(chat_id: int, tracks: list) -> str:
    text = "<blockquote expandable>"
    for track in tracks:
        pos = queue.add(chat_id, track)
        text += f"<b>{pos}.</b> {track.title}\n"
    text = text[:1948] + "</blockquote>"
    return text


@app.on_message(
    filters.command(["play", "playforce", "vplay", "vplayforce"])
    & filters.group
    & ~app.bl_users
)
@lang.language()
@checkUB
async def play_hndlr(
    _,
    m: types.Message,
    force: bool = False,
    video: bool = False,
    url: str = None,
) -> None:
    sent = await m.reply_text(m.lang["play_searching"])
    mention = m.from_user.mention
    media = tg.get_media(m.reply_to_message) if m.reply_to_message else None
    tracks = []
    file = None

    # 🔹 URL PLAY
    if url:
        if "playlist" in url:
            try:
                await sent.edit_text(m.lang["playlist_fetch"])
            except:
                pass

            tracks = await yt.playlist(
                config.PLAYLIST_LIMIT, mention, url, video
            )

            if not tracks:
                try:
                    return await sent.edit_text(m.lang["playlist_error"])
                except:
                    return

            file = tracks[0]
            tracks.remove(file)
            file.message_id = sent.id
        else:
            file = await yt.search(url, sent.id, video=video)

        if not file:
            try:
                return await sent.edit_text(
                    m.lang["play_not_found"].format(config.SUPPORT_CHAT)
                )
            except:
                return

    # 🔹 QUERY PLAY
    elif len(m.command) >= 2:
        query = " ".join(m.command[1:])
        file = await yt.search(query, sent.id, video=video)

        if not file:
            try:
                return await sent.edit_text(
                    m.lang["play_not_found"].format(config.SUPPORT_CHAT)
                )
            except:
                return

    # 🔹 REPLY MEDIA PLAY
    elif media:
        setattr(sent, "lang", m.lang)
        file = await tg.download(m.reply_to_message, sent)

    if not file:
        try:
            return await sent.edit_text(m.lang["play_usage"])
        except:
            return

    # 🔹 DURATION LIMIT SAFE
    if file.duration_sec > config.DURATION_LIMIT:
        try:
            return await sent.edit_text(
                m.lang["play_duration_limit"].format(
                    config.DURATION_LIMIT // 60
                )
            )
        except:
            return

    # 🔹 LOGGER
    if await db.is_logger():
        await utils.play_log(m, file.title, file.duration)

    file.user = mention

    # 🔹 FORCE / QUEUE
    if force:
        queue.force_add(m.chat.id, file)
    else:
        position = queue.add(m.chat.id, file)

        if await db.get_call(m.chat.id):
            try:
                await sent.edit_text(
                    m.lang["play_queued"].format(
                        position,
                        file.url,
                        file.title,
                        file.duration,
                        m.from_user.mention,
                    ),
                    reply_markup=buttons.play_queued(
                        m.chat.id, file.id, m.lang["play_now"]
                    ),
                )
            except:
                await m.reply_text(
                    m.lang["play_queued"].format(
                        position,
                        file.url,
                        file.title,
                        file.duration,
                        m.from_user.mention,
                    )
                )

            if tracks:
                added = playlist_to_queue(m.chat.id, tracks)
                await app.send_message(
                    chat_id=m.chat.id,
                    text=m.lang["playlist_queued"].format(len(tracks)) + added,
                )
            return

    # 🔹 DOWNLOAD IF NEEDED
    if not file.file_path:
        fname = f"downloads/{file.id}.{'mp4' if video else 'webm'}"
        if Path(fname).exists():
            file.file_path = fname
        else:
            try:
                await sent.edit_text(m.lang["play_downloading"])
            except:
                pass

            file.file_path = await yt.download(file.id, video=video)

    # 🔹 PLAY
    await anon.play_media(chat_id=m.chat.id, message=sent, media=file)

    if not tracks:
        return

    added = playlist_to_queue(m.chat.id, tracks)
    await app.send_message(
        chat_id=m.chat.id,
        text=m.lang["playlist_queued"].format(len(tracks)) + added,
    )
