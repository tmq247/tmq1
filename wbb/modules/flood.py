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
from asyncio import get_running_loop, sleep
from time import time

from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from wbb import SUDOERS, app
from wbb.core.decorators.errors import capture_err
from wbb.core.decorators.permissions import adminsOnly
from wbb.modules.admin import list_admins, member_permissions
from wbb.utils.dbfunctions import flood_off, flood_on, is_flood_on
from wbb.utils.filter_groups import flood_group

__MODULE__ = "Flood"
__HELP__ = """
Hệ thống Anti-Flood, người gửi hơn 10 tin nhắn liên tiếp, sẽ bị tắt tiếng trong một giờ (Ngoại trừ quản trị viên).

/flood [ENABLE|DISABLE] - Bật hoặc tắt tính năng phát hiện lũ lụt
"""

DB = {}  # TODO Use mongodb instead of a fucking dict.


def reset_flood(chat_id, user_id=0):
    for user in DB[chat_id].keys():
        if user != user_id:
            DB[chat_id][user] = 0


@app.on_message(
    ~filters.service & ~filters.me & ~filters.private & ~filters.channel & ~filters.bot,
    group=flood_group,
)
@capture_err
async def flood_control_func(_, message: Message):
    if not message.chat:
        return
    chat_id = message.chat.id
    if not (await is_flood_on(chat_id)):
        return
    # Initialize db if not already.
    if chat_id not in DB:
        DB[chat_id] = {}

    if not message.from_user:
        reset_flood(chat_id)
        return

    user_id = message.from_user.id
    mention = message.from_user.mention

    if user_id not in DB[chat_id]:
        DB[chat_id][user_id] = 0

    # Reset flood db of current chat if some other user sends a message
    reset_flood(chat_id, user_id)

    # Ignore devs and admins
    mods = await list_admins(chat_id)
    if user_id in mods or user_id in SUDOERS:
        return

    # Mute if user sends more than 10 messages in a row
    if DB[chat_id][user_id] >= 10:
        DB[chat_id][user_id] = 0
        try:
            await message.chat.restrict_member(
                user_id,
                permissions=ChatPermissions(),
                until_date=int(time() + 3600),
            )
        except Exception:
            return
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="🚨  Bật tiếng  🚨",
                        callback_data=f"Bật tiếng_{user_id}",
                    )
                ]
            ]
        )
        m = await message.reply_text(
            f"Hãy tưởng tượng tràn ngập cuộc trò chuyện trước mặt tôi, Tắt tiếng {mention} trong một giờ!",
            reply_markup=keyboard,
        )

        async def delete():
            await sleep(3600)
            try:
                await m.delete()
            except Exception:
                pass

        loop = get_running_loop()
        return loop.create_task(delete())
    DB[chat_id][user_id] += 1


@app.on_callback_query(filters.regex("unmute_"))
async def flood_callback_func(_, cq: CallbackQuery):
    from_user = cq.from_user
    permissions = await member_permissions(cq.message.chat.id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            "Bạn không có đủ quyền để thực hiện hành động này.\n"
            + f"Quyền cần thiết: {permission}",
            show_alert=True,
        )
    user_id = cq.data.split("_")[1]
    await cq.message.chat.unban_member(user_id)
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += f"__User unmuted by {from_user.mention}__"
    await cq.message.edit(text)


@app.on_message(filters.command("flood") & ~filters.private)
@adminsOnly("can_change_info")
async def flood_toggle(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("Cách sử dụng: /flood [ENABLE|DISABLE]")
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status == "enable":
        await flood_on(chat_id)
        await message.reply_text("Đã bật Trình kiểm tra lũ lụt.")
    elif status == "disable":
        await flood_off(chat_id)
        await message.reply_text("Trình kiểm tra lũ bị vô hiệu hóa.")
    else:
        await message.reply_text("Hậu tố không xác định, sử dụng /flood [ENABLE|DISABLE]")
