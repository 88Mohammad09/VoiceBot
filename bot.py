from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from pydub import AudioSegment
import os
import subprocess

TOKEN = os.environ.get("TOKEN")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 🎤 یک ویس بفرست تا صداتو تغییر بدم.")

# دریافت ویس
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    file_path = "input.ogg"
    await file.download_to_drive(file_path)
    
    context.user_data["voice_file"] = file_path

    keyboard = [
        [InlineKeyboardButton("مرد", callback_data="male")],
        [InlineKeyboardButton("زن", callback_data="female")],
        [InlineKeyboardButton("بچه", callback_data="child")],
        [InlineKeyboardButton("روح", callback_data="ghost")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("میخوای صداتو به چی تغییر بدم؟", reply_markup=reply_markup)

# تغییر pitch با ffmpeg
def pitch_shift_ffmpeg(input_path: str, output_path: str, semitones: float):
    # semitones مثبت → زیرتر، منفی → بم‌تر
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-filter:a", f"asetrate=44100*2^{semitones/12},aresample=44100", 
        output_path
    ], check=True)

# انتخاب دکمه
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    file_path = context.user_data.get("voice_file")
    
    if not file_path:
        await query.edit_message_text("ویسی پیدا نشد. لطفا دوباره ویس بفرست.")
        return

    output_path = "output.ogg"

    if choice == "male":
        pitch_shift_ffmpeg(file_path, output_path, semitones=-4)
    elif choice == "female":
        pitch_shift_ffmpeg(file_path, output_path, semitones=4)
    elif choice == "child":
        pitch_shift_ffmpeg(file_path, output_path, semitones=7)
    elif choice == "ghost":
        pitch_shift_ffmpeg(file_path, output_path, semitones=-12)  # خیلی بم و وهم‌آلود

    await query.edit_message_text(f"صداتو به حالت '{choice}' تغییر دادم!")
    await query.message.reply_voice(voice=open(output_path, "rb"))

# اجرای ربات
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("ربات روشن شد ...")
    app.run_polling()

if __name__ == "__main__":
    main()
