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
from pykeyboard import InlineKeyboard
from pyrogram.types import InlineKeyboardButton as Ikb

from wbb.utils.functions import get_urls_from_text as is_url


def keyboard(buttons_list, row_width: int = 2):
    """
    Trình tạo nút, chuyển các nút trong danh sách và nó sẽ
    trả lại đối tượng pyrogram.types.IKB
    Ví dụ: bàn phím([["bấm vào đây", "https://google.com"]])
    nếu có, một url, nó sẽ tạo nút url, nếu không thì nút gọi lại
    """
    buttons = InlineKeyboard(row_width=row_width)
    data = [
        (
            Ikb(text=str(i[0]), callback_data=str(i[1]))
            if not is_url(i[1])
            else Ikb(text=str(i[0]), url=str(i[1]))
        )
        for i in buttons_list
    ]
    buttons.add(*data)
    return buttons


def ikb(data: dict, row_width: int = 2):
    """
  Chuyển đổi một dict thành các nút pyrogram
    Ví dụ: dict_to_keyboard({"bấm vào đây": "đây là dữ liệu gọi lại"})
    """
    return keyboard(data.items(), row_width=row_width)
