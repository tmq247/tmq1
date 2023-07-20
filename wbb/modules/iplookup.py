import asyncio

from pyrogram import filters
from pyrogram.types import Message

from wbb import app
from wbb.utils import http

# For /help menu
__MODULE__ = "iplookup"
__HELP__ = """
/iplookup [ip address] để có được thông tin chi tiết về ip đó
"""


@app.on_message(filters.command("iplookup"))
async def ip_lookup(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("địa chỉ ip bị thiếu")
    ip_address = message.command[1]
    msg = await message.reply_text("kiểm tra địa chỉ ip...")
    try:
        res = await http.get(f"https://ipinfo.io/{ip_address}/json", timeout=5)
    except asyncio.TimeoutError:
        return await message.reply_text("hết thời gian yêu cầu")
    except Exception as e:
        return await message.reply_text(f"LỖI: `{e}`")
    hostname = res.get("hostname", "N/A")
    city = res.get("city", "N/A")
    region = res.get("region", "N/A")
    country = res.get("country", "N/A")
    location = res.get("loc", "N/A")
    org = res.get("org", "N/A")
    await msg.edit(
        (
            f"**Details of `{ip_address}`**\n\n"
            f"HostName: `{hostname}`\n"
            f"City: `{city}`\n"
            f"Region: `{region}`\n"
            f"Country: `{country}`\n"
            f"Org: `{org}`\n"
            f"Map: https://www.google.fr/maps?q={location}\n"
        ),
        disable_web_page_preview=True,
    )
