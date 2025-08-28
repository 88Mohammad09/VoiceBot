import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
from fastapi import FastAPI, Request
from threading import Thread

# ----------- تنظیمات ربات و درگاه -----------
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
ZARINPAL_MERCHANT_ID = "YOUR_MERCHANT_ID"
ZARINPAL_CALLBACK_URL = "https://YOUR_RAILWAY_URL/payment_callback"

# ----------- دیتابیس ساده با دیکشنری -----------
users = {}  # {user_id: {"credits": 0, "voice_count": 0, "voice_type": "male"}}

# ----------- FastAPI برای وب‌هوک پرداخت -----------
app_api = FastAPI()

@app_api.get("/payment_callback")
async def payment_callback(request: Request):
    user_id = int(request.query_params.get("user_id"))
    status = request.query_params.get("Status")
    authority = request.query_params.get("Authority")

    if status == "OK":
        users.setdefault(user_id, {"credits": 0, "voice_count": 0, "voice_type": "male"})
        users[user_id]["credits"] += 200
        return "پرداخت موفق! 200 امتیاز اضافه شد."
    else:
        return "پرداخت ناموفق!"

def run_api():
    import uvicorn
    uvicorn.run(app_api, host="0.0.0.0", port=8000)

# ----------- توابع ربات تلگرام -----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users.setdefault(user_id, {"credits": 0, "voice_count": 0, "voice_type": "male"})
    keyboard = [
        [InlineKeyboardButton("مرد", callback_data="male"),
         InlineKeyboardButton("زن", callback_data="female")],
        [InlineKeyboardButton("بچه", callback_data="child"),
         InlineKeyboardButton("روح", callback_data="ghost")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! صدای خود را انتخاب کنید:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    users[user_id]["voice_type"] = query.data
    await query.edit_message_text(text=f"صدای شما به {query.data} تغییر کرد!")

async def buy_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    amount = 10000  # تومان
    description = f"خرید 200 امتیاز برای کاربر {user_id}"

    data = {
        "merchant_id": ZARINPAL_MERCHANT_ID,
        "amount": amount,
        "callback_url": f"{ZARINPAL_CALLBACK_URL}?user_id={user_id}",
        "description": description,
        "metadata": {"user_id": user_id}
    }

    response = requests.post("https://api.zarinpal.com/pg/v4/payment/request.json", json=data)
    res_json = response.json()

    if res_json["data"]["code"] == 100:
        payment_url = "https://www.zarinpal.com/pg/StartPay/" + res_json["data"]["authority"]
        await update.message.reply_text(f"برای پرداخت روی لینک زیر کلیک کنید:\n{payment_url}")
    else:
        await update.message.reply_text("خطا در ایجاد پرداخت! دوباره امتحان کنید.")

async def create_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user = users.get(user_id)
    if not user:
        await update.message.reply_text("ابتدا /start را بزنید.")
        return

    if user["voice_count"] >= user["credits"]:
        await update.message.reply_text("امتیاز کافی ندارید! برای خرید امتیاز /buy را بزنید.")
        return

    # اینجا میتونی کد تبدیل صدا واقعی اضافه کنی
    user["voice_count"] += 1
    await update.message.reply_text(f"ویس ساخته شد! ({user['voice_count']}/{user['credits']} استفاده)")

# ----------- اجرای ربات -----------

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("buy", buy_credits))
    app.add_handler(CommandHandler("voice", create_voice))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    Thread(target=run_api).start()
    asyncio.run(main())
