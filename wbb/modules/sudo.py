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
from pyrogram.types import Message

from wbb import BOT_ID, SUDOERS, USERBOT_PREFIX, app2, eor
from wbb.core.decorators.errors import capture_err
from wbb.utils.dbfunctions import add_sudo, get_sudoers, remove_sudo

__MODULE__ = "Sudo"
__HELP__ = """
**THIS MODULE IS ONLY FOR DEVS**

.useradd - Để thêm người dùng trong Sudoers.
.userdel - Để xóa người dùng khỏi Sudoers.
.sudoers - Để liệt kê người dùng Sudo.

**NOTE:**

Không bao giờ thêm bất kỳ ai vào sudoers trừ khi bạn tin tưởng họ,
người dùng sudo có thể làm bất cứ điều gì với tài khoản của bạn, họ
thậm chí có thể xóa tài khoản của bạn.
"""


@app2.on_message(
    filters.command("useradd", prefixes=USERBOT_PREFIX)
    & ~filters.forwarded
    & ~filters.via_bot
    & SUDOERS
)
@capture_err
async def useradd(_, message: Message):
    if not message.reply_to_message:
        return await eor(
            message,
            text="Trả lời tin nhắn của ai đó để thêm anh ta vào sudoers.",
        )
    user_id = message.reply_to_message.from_user.id
    umention = (await app2.get_users(user_id)).mention
    sudoers = await get_sudoers()

    if user_id in sudoers:
        return await eor(message, text=f"{umention} đã có trong sudoers.")
    if user_id == BOT_ID:
        return await eor(message, text="Bạn không thể thêm trợ lý bot trong sudoers.")

    await add_sudo(user_id)

    if user_id not in SUDOERS:
        SUDOERS.add(user_id)

    await eor(
        message,
        text=f"Đã thêm thành công {umention} vào sudoers.",
    )


@app2.on_message(
    filters.command("userdel", prefixes=USERBOT_PREFIX)
    & ~filters.forwarded
    & ~filters.via_bot
    & SUDOERS
)
@capture_err
async def userdel(_, message: Message):
    if not message.reply_to_message:
        return await eor(
            message,
            text="Trả lời tin nhắn của ai đó để xóa anh ta khỏi sudoers.",
        )
    user_id = message.reply_to_message.from_user.id
    umention = (await app2.get_users(user_id)).mention

    if user_id not in await get_sudoers():
        return await eor(message, text=f"{umention}không có trong sudoers.")

    await remove_sudo(user_id)

    if user_id in SUDOERS:
        SUDOERS.remove(user_id)

    await eor(
        message,
        text=f"Đã xóa thành công {umention} khỏi sudoers.",
    )


@app2.on_message(
    filters.command("sudoers", prefixes=USERBOT_PREFIX)
    & ~filters.forwarded
    & ~filters.via_bot
    & SUDOERS
)
@capture_err
async def sudoers_list(_, message: Message):
    sudoers = await get_sudoers()
    text = ""
    j = 0
    for user_id in sudoers:
        try:
            user = await app2.get_users(user_id)
            user = user.first_name if not user.mention else user.mention
            j += 1
        except Exception:
            continue
        text += f"{j}. {user}\n"
    if text == "":
        return await eor(message, text="Không tìm thấy sudoer.")
    await eor(message, text=text)
