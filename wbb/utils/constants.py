# New file

from pyrogram.enums import ChatType, ParseMode
from pyrogram.filters import command
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from wbb import BOT_USERNAME, app

MARKDOWN = """
Đọc kỹ văn bản dưới đây để tìm hiểu cách thức hoạt động của định dạng!

<u>Supported Fillings:</u>

<code>{name}</code> - Điều này sẽ đề cập đến người dùng với tên của họ.
<code>{chat}</code> - Điều này sẽ điền vào tên trò chuyện hiện tại.

LƯU Ý: Điền chỉ hoạt động trong mô-đun lời chào.


<u>Supported formatting:</u>

<code>**Bold**</code> : Điều này sẽ hiển thị dưới dạng văn bản <b>đậm</b>.
<code>~~strike~~</code>: Điều này sẽ hiển thị dưới dạng văn bản <strike>strike</strike>.
<code>__italic__</code>: Điều này sẽ hiển thị dưới dạng văn bản <i>in nghiêng</i>.
<code>--underline--</code>: Điều này sẽ hiển thị dưới dạng văn bản <u>gạch chân</u>.
<code>`code words`</code>: Điều này sẽ hiển thị dưới dạng văn bản <code>code</code>.
<code>||spoiler||</code>: Điều này sẽ hiển thị dưới dạng văn bản <spoiler>Spoiler</spoiler>.
<code>[hyperlink](google.com)</code>: Thao tác này sẽ tạo một văn bản <a href='https://www.google.com'>siêu liên kết</a>.
<b>Note:</b>Bạn có thể sử dụng cả thẻ markdown và html.


<u>Button formatting:</u>

-> text ~ [button text, button link]


<u>Example:</u>

<b>example</b> <i>button with markdown</i> <code>formatting</code> ~ [button text, https://google.com]
"""


@app.on_message(command("markdownhelp"))
async def mkdwnhelp(_, m: Message):
    keyb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Bấm vào đây!",
                    url=f"http://t.me/{BOT_USERNAME}?start=mkdwn_help",
                )
            ]
        ]
    )
    if m.chat.type != ChatType.PRIVATE:
        await m.reply(
            "Nhấp vào nút bên dưới để nhận cú pháp sử dụng markdown trong pm!",
            reply_markup=keyb,
        )
    else:
        await m.reply(
            MARKDOWN, parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )
    return
