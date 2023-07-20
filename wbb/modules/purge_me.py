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

from wbb import SUDOERS, USERBOT_ID, USERBOT_PREFIX, app2, eor, log, telegraph

__MODULE__ = "Userbot"
TEXT = """
<code>alive</code>  →  Gửi tin nhắn còn sống.<br>

<code>create (b|s|c) Title</code>  →  tạo nhóm & kênh [basic|super]<br>

<code>chatbot [ENABLE|DISABLE]</code>  →  Kích hoạt chatbot trong một cuộc trò chuyện.<br>

<code>autocorrect [ENABLE|DISABLE]</code>  →  Điều này sẽ tự động sửa tin nhắn của bạn khi đang di chuyển.<br>

<code>purgeme [Number of messages to purge]</code>  →  Dọn dẹp tin nhắn của riêng bạn.<br>

<code>eval [Lines of code]</code>  →  Thực thi mã Python.<br>

<code>lsTasks</code>  →  Liệt kê các tác vụ đang chạy (eval)<br>

<code>sh [Some shell code]</code>  →  Thực thi mã Shell.<br>

<code>approve</code>  →  Phê duyệt người dùng để PM bạn.<br>

<code>disapprove</code>  →  Từ chối người dùng PM cho bạn.<br>

<code>block</code>  →  Chặn người dùng.<br>

<code>unblock</code>  →  Bỏ chặn người dùng.<br>

<code>anonymize</code>  →  Thay đổi tên/PFP ngẫu nhiên.<br>

<code>impersonate [User_ID|Username|Reply]</code> → Sao chép hồ sơ của người dùng.<br>

<code>useradd</code>  →  Để thêm người dùng trong sudoers. [UNSAFE]<br>

<code>userdel</code>  → Để xóa người dùng khỏi sudoers.<br>

<code>sudoers</code>  →  Để liệt kê người dùng sudo.<br>

<code>download [URL or reply to a file]</code>  →  Tải xuống một tệp từTG or URL<br>

<code>upload [URL or File Path]</code>  →  Tải lên một tập tin từ địa phương hoặc URL<br>

<code>parse_preview [REPLY TO A MESSAGE]</code>  →  Phân tích bản xem trước web_page(link)<br>

<code>id</code>  →  Tương tự như /id nhưng dành cho Ubot<br>

<code>paste</code> → Dán cứt vào batbin.<br>
<code>help</code> → Nhận liên kết đến trang này.<br>

<code>kang</code> → Kang stickers.<br>

<code>dice</code> → Lắc xúc xắc.<br>
"""
log.info("Dán lệnh userbot trên telegraph")

__HELP__ = f"""**Commands:** {telegraph.create_page(
    "Userbot Commands",
    html_content=TEXT,
)['url']}"""

log.info("Đã dán xong các lệnh userbot trên telegraph")


@app2.on_message(
    filters.command("help", prefixes=USERBOT_PREFIX)
    & ~filters.forwarded
    & ~filters.via_bot
    & filters.user(USERBOT_ID)
)
async def get_help(_, message: Message):
    await eor(
        message,
        text=__HELP__,
        disable_web_page_preview=True,
    )


@app2.on_message(
    filters.command(["purgeme", "purge_me"], prefixes=USERBOT_PREFIX)
    & ~filters.forwarded
    & ~filters.via_bot
    & filters.user(USERBOT_ID)
)
async def purge_me_func(_, message: Message):
    if len(message.command) != 2:
        return await message.delete()

    n = message.text.split(None, 1)[1].strip()
    if not n.isnumeric():
        return await eor(message, text="Đối số không hợp lệ")

    n = int(n)

    if n < 1:
        return await eor(message, text="Cần một số >=1")

    chat_id = message.chat.id

    message_ids = [
        m.id
        async for m in app2.search_messages(
            chat_id,
            from_user=int(USERBOT_ID),
            limit=n,
        )
    ]

    if not message_ids:
        return await eor(message, text="Không tìm thấy thư nào.")

   # Một danh sách chứa danh sách 100 đoạn tin nhắn
     # vì chúng tôi không thể xóa hơn 100 tin nhắn cùng lúc,
     # chúng ta phải làm điều đó theo khối 100, tôi sẽ chỉ chọn 99
     # để được an toàn.
    to_delete = [message_ids[i : i + 99] for i in range(0, len(message_ids), 99)]

    for hundred_messages_or_less in to_delete:
        await app2.delete_messages(
            chat_id=chat_id,
            message_ids=hundred_messages_or_less,
            revoke=True,
        )
