import os, sqlite3
from datetime import datetime
import telebot
from telebot.types import Message
from gdrive_utils import upload_to_drive

TOKEN = os.environ.get("TG_BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "123456789"))
DEFAULT_CHANNEL = os.environ.get("DEFAULT_CHANNEL", "@your_channel")
GDRIVE_FOLDER = os.environ.get("GDRIVE_FOLDER_ID")  # Google Drive folder (optional)

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

DB_PATH = "bot_files.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_file_id TEXT,
        file_name TEXT,
        drive_id TEXT,
        drive_link TEXT,
        caption TEXT,
        uploader_id INTEGER,
        created_at TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)""")
    cur.execute("INSERT OR IGNORE INTO admins(user_id) VALUES(?)", (OWNER_ID,))
    conn.commit(); conn.close()

def db_add_file(tg_file_id, file_name, drive_id, drive_link, caption, uploader_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""INSERT INTO files 
        (tg_file_id, file_name, drive_id, drive_link, caption, uploader_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (tg_file_id, file_name, drive_id, drive_link, caption, uploader_id, datetime.utcnow().isoformat()))
    conn.commit(); conn.close()

def db_list_files(limit=20):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, file_name, drive_link, uploader_id FROM files ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall(); conn.close()
    return rows

def db_get_file(fid):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT file_name, drive_link, caption FROM files WHERE id=?", (fid,))
    row = cur.fetchone(); conn.close()
    return row

def is_admin(uid):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM admins WHERE user_id=?", (uid,))
    ok = cur.fetchone() is not None
    conn.close()
    return ok

init_db()

@bot.message_handler(commands=["start"])
def start(m: Message):
    bot.reply_to(m, "আসসালামু আলাইকুম 🌸\nআমার মাধ্যমে ফাইল আপলোড করলে সেটা Google Drive এ যাবে।\n/list দিয়ে তালিকা দেখতে পারো।")

@bot.message_handler(commands=["list"])
def list_files(m: Message):
    rows = db_list_files()
    if not rows:
        bot.reply_to(m, "কোনো ফাইল পাওয়া যায়নি।")
        return
    out = [f"ID:{r[0]} | {r[1]} | {r[2]}" for r in rows]
    bot.reply_to(m, "\n".join(out))

@bot.message_handler(commands=["send"])
def send_file(m: Message):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, "এই কমান্ড admin দের জন্য।")
        return
    parts = m.text.split()
    if len(parts) < 2: return
    try: fid = int(parts[1])
    except: return
    rec = db_get_file(fid)
    if not rec: return
    name, link, cap = rec
    text = f"<b>{name}</b>\n{cap or ''}\n🔗 {link}"
    bot.send_message(DEFAULT_CHANNEL, text)
    bot.reply_to(m, "✅ পাঠানো হয়েছে")

@bot.message_handler(content_types=['document','photo','video','audio'])
def save_file(m: Message):
    try:
        file_info = None; file_name="file"
        if m.document:
            file_info = bot.get_file(m.document.file_id)
            file_name = m.document.file_name
        elif m.photo:
            file_info = bot.get_file(m.photo[-1].file_id)
            file_name="photo.jpg"
        elif m.video:
            file_info = bot.get_file(m.video.file_id)
            file_name = m.video.file_name or "video.mp4"
        elif m.audio:
            file_info = bot.get_file(m.audio.file_id)
            file_name = m.audio.file_name or "audio.mp3"

        if not file_info: return
        file_bytes = bot.download_file(file_info.file_path)

        # Upload to Google Drive
        drive_id, drive_link = upload_to_drive(file_bytes, file_name, folder_id=GDRIVE_FOLDER)

        db_add_file(m.document.file_id if m.document else None, file_name, drive_id, drive_link, m.caption, m.from_user.id)

        bot.reply_to(m, f"✅ Google Drive এ আপলোড হয়েছে!\n{drive_link}")

    except Exception as e:
        bot.reply_to(m, f"❌ সমস্যা হয়েছে: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
