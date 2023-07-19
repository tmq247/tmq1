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
from re import findall

from pyrogram import filters

from wbb import SUDOERS, USERBOT_ID, USERBOT_PREFIX, app, app2, eor
from wbb.core.decorators.errors import capture_err
from wbb.core.decorators.permissions import adminsOnly
from wbb.core.keyboard import ikb
from wbb.utils.dbfunctions import delete_note, get_note, get_note_names, save_note
from wbb.utils.functions import extract_text_and_keyb

__MODULE__ = "Notes"
__HELP__ = """/notes Để nhận tất cả các ghi chú trong cuộc trò chuyện.

/save [NOTE_NAME] Để Lưu Ghi chú (Có thể là nhãn dán hoặc văn bản).

#NOTE_NAME To Get A Note.

/delete [NOTE_NAME] Để Xóa Ghi chú.

Thanh toán /markdownhelp để biết thêm về định dạng và cú pháp khác.
"""


@app2.on_message(
    filters.command("save", prefixes=USERBOT_PREFIX)
    & ~filters.forwarded
    & ~filters.via_bot
    & SUDOERS
)
@app.on_message(filters.command("save") & ~filters.private)
@adminsOnly("can_change_info")
async def save_notee(_, message):
    if len(message.command) < 2 or not message.reply_to_message:
        await eor(
            message,
            text="**Cách sử dụng:**\nTrả lời văn bản hoặc nhãn dán bằng /save [NOTE_NAME] để lưu nó.",
        )

    elif not message.reply_to_message.text and not message.reply_to_message.sticker:
        await eor(
            message,
            text="__**Bạn chỉ có thể lưu văn bản hoặc nhãn dán trong ghi chú.**__",
        )
    else:
        name = message.text.split(None, 1)[1].strip()
        if not name:
            return await eor(message, text="**Cách sử dụng**\n__/save [NOTE_NAME]__")
        _type = "text" if message.reply_to_message.text else "sticker"
        note = {
            "type": _type,
            "data": message.reply_to_message.text.markdown
            if _type == "text"
            else message.reply_to_message.sticker.file_id,
        }
        prefix = message.text.split()[0][0]
        chat_id = message.chat.id if prefix != USERBOT_PREFIX else USERBOT_ID
        await save_note(chat_id, name, note)
        await eor(message, text=f"__**Ghi chú đã lưu {name}.**__")


@app2.on_message(
    filters.command("notes", prefixes=USERBOT_PREFIX)
    & ~filters.forwarded
    & ~filters.via_bot
    & SUDOERS
)
@app.on_message(filters.command("notes") & ~filters.private)
@capture_err
async def get_notes(_, message):
    prefix = message.text.split()[0][0]
    is_ubot = bool(prefix == USERBOT_PREFIX)
    chat_id = USERBOT_ID if is_ubot else message.chat.id

    _notes = await get_note_names(chat_id)

    if not _notes:
        return await eor(message, text="**Không có ghi chú trong cuộc trò chuyện này.**")
    _notes.sort()
    msg = f"List of notes in {'USERBOT' if is_ubot else message.chat.title}\n"
    for note in _notes:
        msg += f"**-** `{note}`\n"
    await eor(message, text=msg)


@app2.on_message(
    filters.command("get", prefixes=USERBOT_PREFIX)
    & ~filters.forwarded
    & ~filters.via_bot
    & SUDOERS
)
async def get_one_note_userbot(_, message):
    if len(message.text.split()) < 2:
        return await eor(message, text="Đối số không hợp lệ")

    name = message.text.split(None, 1)[1]

    _note = await get_note(USERBOT_ID, name)
    if not _note:
        return await eor(message, text="Không có lưu ý như vậy.")

    if _note["type"] == "text":
        data = _note["data"]
        await eor(
            message,
            text=data,
            disable_web_page_preview=True,
        )
    else:
        await message.reply_sticker(_note["data"])


@app.on_message(filters.regex(r"^#.+") & filters.text & ~filters.private)
@capture_err
async def get_one_note(_, message):
    name = message.text.replace("#", "", 1)
    if not name:
        return
    _note = await get_note(message.chat.id, name)
    if not _note:
        return
    if _note["type"] == "text":
        data = _note["data"]
        keyb = None
        if findall(r"\[.+\,.+\]", data):
            keyboard = extract_text_and_keyb(ikb, data)
            if keyboard:
                data, keyb = keyboard
        await message.reply_text(
            data,
            reply_markup=keyb,
            disable_web_page_preview=True,
        )
    else:
        await message.reply_sticker(_note["data"])


@app2.on_message(
    filters.command("delete", prefixes=USERBOT_PREFIX)
    & ~filters.forwarded
    & ~filters.via_bot
    & SUDOERS
)
@app.on_message(filters.command("delete") & ~filters.private)
@adminsOnly("can_change_info")
async def del_note(_, message):
    if len(message.command) < 2:
        return await eor(message, text="**Cách sử dụng**\n__/delete [NOTE_NAME]__")
    name = message.text.split(None, 1)[1].strip()
    if not name:
        return await eor(message, text="**Cách sử dụng**\n__/delete [NOTE_NAME]__")

    prefix = message.text.split()[0][0]
    is_ubot = bool(prefix == USERBOT_PREFIX)
    chat_id = USERBOT_ID if is_ubot else message.chat.id

    deleted = await delete_note(chat_id, name)
    if deleted:
        await eor(message, text=f"**Đã xóa ghi chú {name} thành công.**")
    else:
        await eor(message, text="**Không có lưu ý như vậy.**")
