from asyncio import get_event_loop, sleep

from feedparser import parse
from pyrogram import filters
from pyrogram.errors import (
    ChannelInvalid,
    ChannelPrivate,
    InputUserDeactivated,
    UserIsBlocked,
)
from pyrogram.types import Message

from wbb import RSS_DELAY, app, log
from wbb.core.decorators.errors import capture_err
from wbb.utils.dbfunctions import (
    add_rss_feed,
    get_rss_feeds,
    is_rss_active,
    remove_rss_feed,
    update_rss_feed,
)
from wbb.utils.functions import get_http_status_code, get_urls_from_text
from wbb.utils.rss import Feed

__MODULE__ = "RSS"
__HELP__ = f"""
/add_feed [URL] - Thêm một nguồn cấp dữ liệu để trò chuyện
/rm_feed - Xóa nguồn cấp dữ liệu khỏi cuộc trò chuyện

**Note:**
    -Điều này sẽ kiểm tra các bản cập nhật {RSS_DELAY // 60} phút một lần.
     - Bạn chỉ có thể thêm một nguồn cấp dữ liệu cho mỗi cuộc trò chuyện.
     - Hiện tại nguồn cấp dữ liệu RSS và ATOM được hỗ trợ.
"""


async def rss_worker():
    log.info("RSS Worker started")
    while True:
        feeds = await get_rss_feeds()
        if not feeds:
            await sleep(RSS_DELAY)
            continue

        loop = get_event_loop()

        for _feed in feeds:
            chat = _feed["chat_id"]
            try:
                url = _feed["url"]
                last_title = _feed.get("last_title")

                parsed = await loop.run_in_executor(None, parse, url)
                feed = Feed(parsed)

                if feed.title == last_title:
                    continue

                await app.send_message(
                    chat, feed.parsed(), disable_web_page_preview=True
                )
                await update_rss_feed(chat, feed.title)
            except (
                ChannelInvalid,
                ChannelPrivate,
                InputUserDeactivated,
                UserIsBlocked,
                AttributeError,
            ):
                await remove_rss_feed(chat)
                log.info(f"Removed RSS Feed from {chat} (Invalid Chat)")
            except Exception as e:
                log.info(f"RSS in {chat}: {str(e)}")
        await sleep(RSS_DELAY)


loop = get_event_loop()
loop.create_task(rss_worker())


@app.on_message(filters.command("add_feed"))
@capture_err
async def add_feed_func(_, m: Message):
    if len(m.command) != 2:
        return await m.reply("Đọc 'RSS' phần trong menu trợ giúp.")
    url = m.text.split(None, 1)[1].strip()

    if not url:
        return await m.reply("[LỖI]: Đối số không hợp lệ")

    urls = get_urls_from_text(url)
    if not urls:
        return await m.reply("[LỖI]: URL không hợp lệ")

    url = urls[0]
    status = await get_http_status_code(url)
    if status != 200:
        return await m.reply("[LỖI]: Url không hợp lệ")

    ns = "[LỖI]: Nguồn cấp dữ liệu này không được hỗ trợ."
    try:
        loop = get_event_loop()
        parsed = await loop.run_in_executor(None, parse, url)
        feed = Feed(parsed)
    except Exception:
        return await m.reply(ns)
    if not feed:
        return await m.reply(ns)

    chat_id = m.chat.id
    if await is_rss_active(chat_id):
        return await m.reply("[LỖI]: Bạn đã bật nguồn cấp dữ liệu RSS.")
    try:
        await m.reply(feed.parsed(), disable_web_page_preview=True)
    except Exception:
        return await m.reply(ns)
    await add_rss_feed(chat_id, parsed.url, feed.title)


@app.on_message(filters.command("rm_feed"))
async def rm_feed_func(_, m: Message):
    if await is_rss_active(m.chat.id):
        await remove_rss_feed(m.chat.id)
        await m.reply("Nguồn cấp dữ liệu RSS đã bị xóa")
    else:
        await m.reply("Không có Nguồn cấp RSS nào đang hoạt động trong cuộc trò chuyện này.")
