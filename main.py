import logging
import os
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "8996389717:AAFMA08thcZh_sDyQwsqk_XcFTS6y8z2skQ")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "JARVIS & Ultron Core Server: ON"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

user_reminders = []

def main_keyboard():
    keyboard = [
        [KeyboardButton("📊 Tizim Holati"), KeyboardButton("📋 Eslatmalar")],
        [KeyboardButton("🔹 JARVIS bilan muloqot"), KeyboardButton("🔴 Ultron Rejimi")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 **JARVIS & Ultron Ekosistemasi Onlayn!**\n\n"
        "🔹 **JARVIS:** Serverga muvaffaqiyatli ulanganmiz, xo'jayin. 24/7 rejim faol.\n"
        "🔴 **Ultron:** Xavfsizlik va resurslar nazorati ta'minlandi.\n\n"
        "Menyudan kerakli bo'limni tanlang."
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=main_keyboard())

async def add_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("🔹 **JARVIS:** Xo'jayin, eslatma matnini kiriting. Masalan: `/remind Soat 5 da uchrashuv bor`", parse_mode='Markdown')
        return
    
    user_reminders.append(text)
    await update.message.reply_text(f"🔹 **JARVIS:** Eslatma xotiraga saqlandi: \"{text}\"", parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📊 Tizim Holati":
        reply = "📊 **Tizim Holati:** Server Onlayn ✅ (24/7 Cloud Host)"
    elif text == "📋 Eslatmalar":
        reply = f"📋 **Eslatmalar:**\n" + "\n".join([f"{i+1}. {r}" for i, r in enumerate(user_reminders)]) if user_reminders else "🔹 Eslatmalar yo'q."
    else:
        reply = f"🔹 **JARVIS:** Buyruq tahlil qilinmoqda: \"{text}\""
    
    await update.message.reply_text(reply, parse_mode='Markdown', reply_markup=main_keyboard())

if __name__ == '__main__':
    keep_alive()
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("remind", add_reminder))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("JARVIS & Ultron Serverda ishga tushmoqda...")
    bot_app.run_polling()

