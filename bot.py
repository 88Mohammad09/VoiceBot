import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from pydub import AudioSegment
import os

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # جایگزین کن
DB_FILE = "users.db"

# ایجاد دیتابیس و جدول کاربران
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, voices_used INTEGER DEFAULT 0)''')
conn.commit()
conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
    conn.commit()
    c.execute("SELECT points, voices_used FROM users WHERE user_id=?", (user_id,))
    points, voices_used = c.fetchone()
    conn.close()

    keyboard = [
        [InlineKeyboardButton("مرد", callback_data="male"),
         InlineKeyboardButton("زن", callback_data="female")],
        [InlineKeyboardButton("کودک", callback_data="child"),
         InlineKeyboardButton("روح", callback_data="ghost")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"سلام!\nامتیاز شما: {points}\nویس استفاده شده: {voices_used}\nکدوم صدا رو میخوای؟",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    # اینجا تبدیل صدا انجام میشه
    voice_path = os.path.join("voices", f"{choice}.mp3")
    if os.path.exists(voice_path):
        await query.edit_message_text(text=f"صدا انتخاب شد: {choice}")
        # میتونی اینجا صدا رو پردازش کنی و ویس خروجی بسازی
    else:
        await query.edit_message_text(text="صدا موجود نیست!")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    await app.start_polling()
    await app.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
