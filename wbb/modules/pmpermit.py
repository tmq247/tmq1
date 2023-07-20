"""
MIT License

Copyright (c) 2023 TheHamkerCat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from pyrogram import filters
from pyrogram.raw.functions.messages import DeleteHistory

from wbb import BOT_ID, PM_PERMIT, SUDOERS, USERBOT_ID, USERBOT_PREFIX, app, app2, eor
from wbb.core.decorators.errors import capture_err
from wbb.utils.dbfunctions import (
    approve_pmpermit,
    disapprove_pmpermit,
    is_pmpermit_approved,
)

flood = {}


@app2.on_message(
    filters.private
    & filters.incoming
    & ~filters.service
    & ~filters.me
    & ~filters.bot
    & ~filters.via_bot
    & ~SUDOERS
)
@capture_err
async def pmpermit_func(_, message):
    user_id = message.from_user.id
    if not PM_PERMIT or await is_pmpermit_approved(user_id):
        return
    async for m in app2.get_chat_history(user_id, limit=6):
        if m.reply_markup:
            await m.delete()
    if str(user_id) in flood:
        flood[str(user_id)] += 1
    else:
        flood[str(user_id)] = 1
    if flood[str(user_id)] > 5:
        await message.reply_text("PHÁT HIỆN SPAM, TỰ ĐỘNG CHẶN NGƯỜI DÙNG!")
        return await app2.block_user(user_id)
    results = await app2.get_inline_bot_results(BOT_ID, f"pmpermit {user_id}")
    await app2.send_inline_bot_result(
        user_id,
        results.query_id,
        results.results[0].id,
    )


@app2.on_message(
    filters.command("approve", prefixes=USERBOT_PREFIX)
    & SUDOERS 
    & ~filters.via_bot
    & ~filters.forwarded
)
@capture_err
async def pm_approve(_, message):
    if not message.reply_to_message:
        return await eor(message, text="Trả lời tin nhắn của người dùng để phê duyệt.")
    user_id = message.reply_to_message.from_user.id
    if await is_pmpermit_approved(user_id):
        return await eor(message, text="Người dùng đã được phê duyệt để pm")
    await approve_pmpermit(user_id)
    await eor(message, text="Người dùng được phê duyệt để pm")


@app2.on_message(
    filters.command("disapprove", prefixes=USERBOT_PREFIX)
    & SUDOERS 
    & ~filters.via_bot
    & ~filters.forwarded
)
async def pm_disapprove(_, message):
    if not message.reply_to_message:
        return await eor(message, text="Trả lời tin nhắn của người dùng để từ chối.")
    user_id = message.reply_to_message.from_user.id
    if not await is_pmpermit_approved(user_id):
        await eor(message, text="Người dùng đã bị từ chối pm")
        async for m in app2.get_chat_history(user_id, limit=6):
            if m.reply_markup:
                try:
                    await m.delete()
                except Exception:
                    pass
        return
    await disapprove_pmpermit(user_id)
    await eor(message, text="Người dùng bị từ chối pm")


@app2.on_message(
    filters.command("block", prefixes=USERBOT_PREFIX)
    & SUDOERS
    & ~filters.via_bot
    & ~filters.forwarded
)
@capture_err
async def block_user_func(_, message):
    if not message.reply_to_message:
        return await eor(message, text="Trả lời tin nhắn của người dùng để chặn.")
    user_id = message.reply_to_message.from_user.id
    # Chặn người dùng sau khi chỉnh sửa tin nhắn để người khác có thể nhận được bản cập nhật.
    await eor(message, text="Đã chặn người dùng thành công")
    await app2.block_user(user_id)


@app2.on_message(
    filters.command("unblock", prefixes=USERBOT_PREFIX)
    & SUDOERS 
    & ~filters.via_bot
    & ~filters.forwarded
)
async def unblock_user_func(_, message):
    if not message.reply_to_message:
        return await eor(message, text="Trả lời tin nhắn của người dùng để bỏ chặn.")
    user_id = message.reply_to_message.from_user.id
    await app2.unblock_user(user_id)
    await eor(message, text="Đã bỏ chặn người dùng thành công")


# CALLBACK QUERY HANDLER

flood2 = {}


@app.on_callback_query(filters.regex("pmpermit"))
async def pmpermit_cq(_, cq):
    user_id = cq.from_user.id
    data, victim = (
        cq.data.split(None, 2)[1],
        cq.data.split(None, 2)[2],
    )
    if data == "approve":
        if user_id != USERBOT_ID:
            return await cq.answer("Nút này không dành cho bạn")
        await approve_pmpermit(int(victim))
        return await app.edit_inline_text(
            cq.inline_message_id, "Người dùng đã được chấp thuận cho PM."
        )

    if data == "block":
        if user_id != USERBOT_ID:
            return await cq.answer("Nút này không dành cho bạn")
        await cq.answer()
        await app.edit_inline_text(
            cq.inline_message_id, "Đã chặn người dùng thành công."
        )
        await app2.block_user(int(victim))
        return await app2.invoke(
            DeleteHistory(
                peer=(await app2.resolve_peer(victim)),
                max_id=0,
                revoke=False,
            )
        )

    if user_id == USERBOT_ID:
        return await cq.answer("Nó Dành Cho Người Khác.")

    if data == "to_scam_you":
        async for m in app2.get_chat_history(user_id, limit=6):
            if m.reply_markup:
                await m.delete()
        await app2.send_message(user_id, "Bị chặn, Đi lừa đảo người khác.")
        await app2.block_user(user_id)
        await cq.answer()

    elif data == "approve_me":
        await cq.answer()
        if str(user_id) in flood2:
            flood2[str(user_id)] += 1
        else:
            flood2[str(user_id)] = 1
        if flood2[str(user_id)] > 5:
            await app2.send_message(user_id, "SPAM ĐÃ PHÁT HIỆN, NGƯỜI DÙNG ĐÃ CHẶN.")
            return await app2.block_user(user_id)
        await app2.send_message(
            user_id,
            "Tôi đang bận, sẽ phê duyệt bạn ngay, KHÔNG SPAM.",
        )
