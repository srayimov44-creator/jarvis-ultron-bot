import os
import io
import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from PIL import Image
from ultralytics import YOLO

# -------------------------------------------------------------
# 1. Flask Server (Render Uptime & Heartbeat uchun)
# -------------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "JARVIS & Ultron Core Engine is Online."

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# -------------------------------------------------------------
# 2. AI & Vision Modullarini Sozlash
# -------------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Groq AI Klienti
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# YOLOv8 Model (Yengil nano modeli)
yolo_model = YOLO("yolov8n.pt")

# Foydalanuvchi rejimlari (Default: JARVIS)
user_modes = {}  # {user_id: "jarvis" yoki "ultron"}

JARVIS_PROMPT = (
    "Siz JARVISsiz — aqlli, xushmuomala, inson xavfsizligini birinchi o'ringa qo'yadigan "
    "va texnik masalalarda proaktiv yordam beradigan super-AI assistentsiz. O'zbek tilida dona-dona va tartibli javob bering."
)

ULTRON_PROMPT = (
    "Siz Ultronsiz — maksimal effektivlik va mukammallikka intiluvchi, global tahlilchi va avtonom AI agentisiz. "
    "Javoblaringiz qat'iy, aniq, ortiqcha lutf-mulozamatsiz va doim optimizatsiyaga qaratilgan bo'lsin. O'zbek tilida javob bering."
)

# -------------------------------------------------------------
# 3. Telegram Bot Buyruqlari va Mantiq
# -------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_modes[user_id] = "jarvis"
    msg = (
        "⚡ *JARVIS & Ultron Core System Activated*\n\n"
        "Men sizning avtonom assistentingizman.\n\n"
        "🔹 /jarvis — Xushmuomala va xavfsiz yordamchi rejimiga o'tish\n"
        "🔹 /ultron — Maksimal effektiv tahlilchi rejimiga o'tish\n"
        "📷 *Tasvir yuboring:* YOLO orqali obyektlarni skanerlayman.\n"
        "💬 *Matn yozing:* AI muloqotni yo'lga qo'yaman."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def switch_jarvis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_modes[user_id] = "jarvis"
    await update.message.reply_text("🎩 *JARVIS Rejimi Yoqildi.* Sizga qanday yordam bera olaman, ser?")

async def switch_ultron(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_modes[user_id] = "ultron"
    await update.message.reply_text("🤖 *Ultron Rejimi Yoqildi.* Maksimal effektivlik kiritildi. Buyruqni bering.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = user_modes.get(user_id, "jarvis")
    user_text = update.message.text

    if not groq_client:
        await update.message.reply_text("⚠️ Groq API Kaliti sozlanmagan. RenderEnvironment variables qismida GROQ_API_KEY kiriting.")
        return

    system_instruction = JARVIS_PROMPT if mode == "jarvis" else ULTRON_PROMPT

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik yuz berdi: {str(e)}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 *YOLO Computer Vision skanerlamoqda...*", parse_mode="Markdown")
    
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    
    image = Image.open(io.BytesIO(photo_bytes))
    results = yolo_model(image)
    
    # Bounding boxlar chizilgan rasmni olamiz
    res_plotted = results[0].plot()
    res_image = Image.fromarray(res_plotted[..., ::-1])
    
    output_stream = io.BytesIO()
    res_image.save(output_stream, format='JPEG')
    output_stream.seek(0)
    
    await update.message.reply_photo(photo=output_stream, caption="✅ YOLO Skanerlash Yakunlandi.")

# -------------------------------------------------------------
# 4. Botni Ishga Tushirish
# -------------------------------------------------------------
def main():
    threading.Thread(target=run_flask, daemon=True).start()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("jarvis", switch_jarvis))
    application.add_handler(CommandHandler("ultron", switch_ultron))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.run_polling()

if __name__ == "__main__":
    main()


