from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pydub import AudioSegment
import os

# گرفتن TOKEN از Environment Variable
TOKEN = os.environ.get("TOKEN")

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 🎤 یک ویس بفرست تا صداشو تغییر بدم.")

# پردازش ویس
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    file_path = "input.ogg"
    await file.download_to_drive(file_path)

    # تبدیل به wav و اعمال افکت
    sound = AudioSegment.from_file(file_path, format="ogg")
    new_sound = sound._spawn(sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * 1.5)})
    new_sound = new_sound.set_frame_rate(44100)

    output_path = "output.ogg"
    new_sound.export(output_path, format="ogg")

    await update.message.reply_voice(voice=open(output_path, "rb"))

# اجرای ربات
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    print("ربات روشن شد ...")
    app.run_polling()

if __name__ == "__main__":
    main()
