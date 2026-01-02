# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

import os
import re
import yt_dlp
import random
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Union

from pyrogram import enums, types
from py_yt import Playlist, VideosSearch

from anony import logger
from anony.helpers import Track, utils


class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = False
        self.warned = False
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )

    # ---------------- COOKIES ---------------- #

    def get_cookies(self):
        if not self.checked:
            if os.path.isdir("anony/cookies"):
                for file in os.listdir("anony/cookies"):
                    if file.endswith(".txt"):
                        self.cookies.append(file)
            self.checked = True

        if not self.cookies:
            if not self.warned:
                self.warned = True
                logger.warning("Cookies are missing; downloads might fail.")
            return None

        return f"anony/cookies/{random.choice(self.cookies)}"

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("Saving cookies from urls...")
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    path = f"anony/cookies/cookie{random.randint(10000, 99999)}.txt"
                    link = url.replace("me/", "me/raw/")
                    async with session.get(link) as resp:
                        resp.raise_for_status()
                        with open(path, "wb") as fw:
                            fw.write(await resp.read())
                except Exception as e:
                    logger.error("Cookie save failed: %s", e)
        logger.info("Cookies saved.")

    # ---------------- URL ---------------- #

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    def url(self, message_1: types.Message) -> Union[str, None]:
        link = None
        messages = [message_1]
        entities = [enums.MessageEntityType.URL, enums.MessageEntityType.TEXT_LINK]

        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            text = message.text or message.caption or ""

            if message.entities:
                for entity in message.entities:
                    if entity.type in entities:
                        link = entity.url
                        break

            if message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type in entities:
                        link = entity.url
                        break

        if link:
            return link.split("&si")[0].split("?si")[0]
        return None

    # ---------------- SEARCH ---------------- #

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        try:
            _search = VideosSearch(query, limit=1)
            results = await _search.next()
        except Exception as e:
            logger.error("YouTube search failed: %s", e)
            return None

        if not results or not results.get("result"):
            return None

        data = results["result"][0]

        duration = data.get("duration")
        duration_sec = utils.to_seconds(duration) if duration else 0

        # ❌ Live / shorts skip
        if duration_sec == 0:
            return None

        return Track(
            id=data.get("id"),
            channel_name=data.get("channel", {}).get("name", ""),
            duration=duration or "0:00",
            duration_sec=duration_sec,
            message_id=m_id,
            title=(data.get("title") or "Unknown")[:25],
            thumbnail=(
                data.get("thumbnails", [{}])[-1].get("url", "").split("?")[0]
            ),
            url=data.get("link"),
            view_count=data.get("viewCount", {}).get("short", ""),
            video=video,
        )

    # ---------------- PLAYLIST ---------------- #

    async def playlist(
        self, limit: int, user: str, url: str, video: bool
    ) -> list[Track]:
        tracks = []

        try:
            plist = await Playlist.get(url)
        except Exception as e:
            logger.error("Playlist fetch failed: %s", e)
            return tracks

        for data in plist.get("videos", [])[:limit]:
            duration = data.get("duration")
            duration_sec = utils.to_seconds(duration) if duration else 0

            # ❌ skip live / broken
            if duration_sec == 0:
                continue

            try:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=duration or "0:00",
                    duration_sec=duration_sec,
                    title=(data.get("title") or "Unknown")[:25],
                    thumbnail=data.get("thumbnails", [{}])[-1]
                    .get("url", "")
                    .split("?")[0],
                    url=data.get("link", "").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
            except Exception:
                continue

        return tracks

    # ---------------- DOWNLOAD ---------------- #

    async def download(self, video_id: str, video: bool = False) -> Optional[str]:
        url = self.base + video_id
        ext = "mp4" if video else "webm"
        filename = f"downloads/{video_id}.{ext}"

        if Path(filename).exists():
            return filename

        cookie = self.get_cookies()
        base_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "no_warnings": True,
            "overwrites": False,
            "nocheckcertificate": True,
            "cookiefile": cookie,
        }

        if video:
            ydl_opts = {
                **base_opts,
                "format": "(bestvideo[height<=?720][ext=mp4])+(bestaudio)",
                "merge_output_format": "mp4",
            }
        else:
            ydl_opts = {
                **base_opts,
                "format": "bestaudio[ext=webm][acodec=opus]",
            }

        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([url])
                except (yt_dlp.utils.DownloadError, yt_dlp.utils.ExtractorError):
                    if cookie in self.cookies:
                        self.cookies.remove(cookie)
                    return None
                except Exception as ex:
                    logger.error("Download failed: %s", ex)
                    return None
            return filename

        return await asyncio.to_thread(_download)
