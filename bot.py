import os
import json
import telebot
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaInMemoryUpload

# Environment variables
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
DEFAULT_CHANNEL = os.environ.get("DEFAULT_CHANNEL", "")

# 🔹 Google Drive credentials from GitHub Secret
creds_json_str = os.environ.get("GDRIVE_JSON")
creds_dict = json.loads(creds_json_str)
creds = service_account.Credentials.from_service_account_info(
    creds_dict, scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=creds)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Commands
@bot.message_handler(commands=["start"])
def start_msg(m):
    bot.reply_to(m, "আসসালামু আলাইকুম! আমি Google Drive ফাইল-শেয়ারিং বট।")

@bot.message_handler(commands=["help"])
def help_msg(m):
    bot.reply_to(m, "/share <link> → Google Drive link share\n/upload (reply with file) → Upload to Drive\n/post <text> → Post to channel (Owner only)")

# Share Google Drive Link
@bot.message_handler(commands=["share"])
def share_file(m):
    parts = m.text.split()
    if len(parts) < 2:
        bot.reply_to(m, "⚠️ লিঙ্ক দিতে হবে! Usage: /share <link>")
        return
    link = parts[1]
    bot.reply_to(m, f"✅ ফাইল শেয়ার হয়েছে:\n{link}")

# Upload file to Drive (reply to document)
@bot.message_handler(commands=["upload"])
def upload_file(m):
    if not m.reply_to_message or not m.reply_to_message.document:
        bot.reply_to(m, "⚠️ কোনো ফাইলের reply দিতে হবে।")
        return

    file_info = bot.get_file(m.reply_to_message.document.file_id)
    file_data = bot.download_file(file_info.file_path)
    file_name = m.reply_to_message.document.file_name

    media = MediaInMemoryUpload(file_data, resumable=True)
    file_metadata = {"name": file_name}
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    file_id = uploaded_file.get("id")
    file_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

    bot.reply_to(m, f"✅ ফাইল Google Drive এ আপলোড হয়েছে:\n{file_link}")

# Post to channel (Owner only)
@bot.message_handler(commands=["post"])
def post_channel(m):
    if m.from_user.id != OWNER_ID:
        bot.reply_to(m, "❌ অনুমতি নেই!")
        return
    text = m.text.replace("/post", "").strip()
    if text:
        bot.send_message(DEFAULT_CHANNEL, text)
        bot.reply_to(m, "✅ চ্যানেলে পোস্ট হয়েছে।")
    else:
        bot.reply_to(m, "⚠️ কিছু লিখো!")

print("🤖 Bot is running...")
bot.infinity_polling()
