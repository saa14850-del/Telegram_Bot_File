# 📂 Telegram File Sharing Bot

এটি একটি টেলিগ্রাম বট, যা দিয়ে:
- ✅ Google Drive লিঙ্ক শেয়ার করা যাবে
- ✅ টেলিগ্রাম চ্যানেলে পোস্ট করা যাবে
- ✅ টেলিগ্রাম গ্রুপ ম্যানেজ করা যাবে
- ✅ GitHub Actions দিয়ে স্বয়ংক্রিয়ভাবে রান হবে

---

## 🚀 Setup Guide

### 1. Bot তৈরি
- Telegram এ [@BotFather](https://t.me/BotFather) দিয়ে বট তৈরি করো
- BotFather থেকে **API Token** নাও

### 2. GitHub Secrets সেট করো
GitHub Repo → **Settings → Secrets and variables → Actions**
- `TG_BOT_TOKEN` → BotFather টোকেন
- `OWNER_ID` → তোমার Telegram user ID
- `DEFAULT_CHANNEL` → `@channelusername`

### 3. Workflow চালাও
- Repo → **Actions** → `Run Telegram Bot` → **Run workflow**

---

## 📌 Commands

- `/start` → বট শুরু করো  
- `/help` → হেল্প মেনু দেখাও  
- `/share <Google Drive Link>` → ফাইল লিঙ্ক শেয়ার করো  
- `/post <text>` → চ্যানেলে পোস্ট করো (Owner only)  

---

## ⚙️ Tech Stack
- Python 3.11
- [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/)
- GitHub Actions (CI/CD)

---

## 📜 License
MIT License
