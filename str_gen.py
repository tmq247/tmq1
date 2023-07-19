from pyrogram import Client as c

API_ID = input("\nNhập API_ID của bạn:\n > ")
API_HASH = input("\nNhập API_HASH của bạn:\n > ")

print("\n\n Nhập số điện thoại khi được hỏi.\n\n")

i = c("wbb", api_id=API_ID, api_hash=API_HASH, in_memory=True)

with i:
    ss = i.export_session_string()
    print("\nĐÂY LÀ PHIÊN CHUỖI CỦA BẠN, SAO CHÉP NÓ, KHÔNG CHIA SẺ!!\n")
    print(f"\n{ss}\n")
