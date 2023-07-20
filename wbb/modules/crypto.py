from pyrogram import filters

from wbb import app
from wbb.core.decorators.errors import capture_err
from wbb.core.keyboard import ikb
from wbb.core.sections import section
from wbb.utils.http import get

__MODULE__ = "Crypto"
__HELP__ = """
/crypto [currency]
        Nhận giá trị Thời gian thực từ loại tiền được cung cấp.
"""


@app.on_message(filters.command("crypto"))
@capture_err
async def crypto(_, message):
    if len(message.command) < 2:
        return await message.reply("/crypto [currency]")

    currency = message.text.split(None, 1)[1].lower()

    btn = ikb(
        {"Tiền tệ khả dụng": "https://plotcryptoprice.herokuapp.com"},
    )

    m = await message.reply("`Đang xử lý...`")

    try:
        r = await get(
            "https://x.wazirx.com/wazirx-falcon/api/v2.0/crypto_rates",
            timeout=5,
        )
    except Exception:
        return await m.edit("[LỖI]: Đã xảy ra sự cố.")

    if currency not in r:
        return await m.edit(
            "[LỖI]: TIỀN TỆ KHÔNG HỢP LỆ",
            reply_markup=btn,
        )

    body = {i.upper(): j for i, j in r.get(currency).items()}

    text = section(
        "Tỷ giá tiền điện tử hiện tại cho " + currency.upper(),
        body,
    )
    await m.edit(text, reply_markup=btn)
