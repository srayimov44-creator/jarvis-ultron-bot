import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Token to'g'ridan-to'g'ri kiritildi
TOKEN = os.environ.get(
    'BOT_TOKEN', '8996389717:AAFVz7HtLEY5gIrDw5M83USGYjmP-0zOU7Q'
)
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

# Foydalanuvchilarning joriy rejimini saqlash uchun lug'at
user_modes = {}


@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
  data = request.get_json()

  if data and 'message' in data:
    message = data['message']
    chat_id = message['chat']['id']
    text = message.get('text', '')

    # Rejimni o'zgartirish buyruqlari
    if text == '/jarvis':
      user_modes[chat_id] = 'jarvis'
      send_message(
          chat_id,
          '🎩 *JARVIS Rejimi Yoqildi.* Sizga qanday yordam bera olaman, ser?',
      )
    elif text == '/ultron':
      user_modes[chat_id] = 'ultron'
      send_message(
          chat_id,
          '🤖 *Ultron Rejimi Yoqildi.* Maksimal effektivlik kiritildi. Buyruqni'
          ' bering.',
      )
    else:
      # Foydalanuvchi qaysi rejimdaligini tekshirish (standart: jarvis)
      mode = user_modes.get(chat_id, 'jarvis')

      if mode == 'jarvis':
        reply = (
            f'🎩 *JARVIS:* Buyrugʻingiz qabul qilindi, ser. Buni koʻrib chiqaman:'
            f' "{text}"'
        )
      else:
        reply = (
            f'🤖 *ULTRON:* Tahlil qilindi. Optimal bajarish jarayoni boshlandi:'
            f' "{text}"'
        )

      send_message(chat_id, reply)

  return 'OK', 200


def send_message(chat_id, text):
  payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
  try:
    requests.post(TELEGRAM_API_URL, json=payload)
  except Exception as e:
    print(f'Xatolik yuz berdi: {e}')


@app.route('/')
def home():
  return 'Bot faol holatda va ishlamoqda!', 200


if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)

