import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import telebot
from telebot import types

TOKEN = "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН"
GROUP_ID = -4871965571

bot = telebot.TeleBot(TOKEN)
user_data = {}

texts = {
    "ru": {
        "choose_language": "Пожалуйста, выберите язык:",
        "phone": "Пожалуйста, отправьте свой номер телефона.",
        "phone_button": "Отправить номер телефона",
        "phone_error": "Пожалуйста, используйте кнопку ниже, чтобы отправить номер телефона.",
        "name": "Пожалуйста, введите ваше полное имя.",
        "direction": "Пожалуйста, укажите направление обучения.",
        "group": "Пожалуйста, укажите номер вашей учебной группы.",
        "appeal": "Пожалуйста, напишите своё обращение.",
        "done": "✅ Спасибо! Ваше обращение зарегистрировано. По вашему обращению с вами свяжутся."
    },
    "uz": {
        "choose_language": "Iltimos, tilni tanlang:",
        "phone": "Iltimos, telefon raqamingizni yuboring.",
        "phone_button": "Telefon raqamini yuborish",
        "phone_error": "Iltimos, telefon raqamingizni yuborish uchun quyidagi tugmadan foydalaning.",
        "name": "Iltimos, to‘liq ism-familiyangizni kiriting.",
        "direction": "Iltimos, ta’lim yo‘nalishingizni kiriting.",
        "group": "Iltimos, o‘quv guruhingiz raqamini kiriting.",
        "appeal": "Iltimos, murojaatingizni yozing.",
        "done": "✅ Rahmat! Murojaatingiz ro‘yxatga olindi. Murojaatingiz bo‘yicha siz bilan bog‘lanishadi."
    },
    "en": {
        "choose_language": "Please choose a language:",
        "phone": "Please share your phone number.",
        "phone_button": "Share phone number",
        "phone_error": "Please use the button below to share your phone number.",
        "name": "Please enter your full name.",
        "direction": "Please specify your field of study.",
        "group": "Please enter your study group number.",
        "appeal": "Please write your message.",
        "done": "✅ Thank you! Your request has been registered. You will be contacted regarding your request."
    }
}


def send_language_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Русский", "O‘zbekcha", "English")
    bot.send_message(chat_id, texts["ru"]["choose_language"], reply_markup=markup)


def send_phone_request(chat_id, lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton(texts[lang]["phone_button"], request_contact=True)
    markup.add(button)
    bot.send_message(chat_id, texts[lang]["phone"], reply_markup=markup)


@bot.message_handler(commands=["start"])
def start_handler(message):
    user_data[message.chat.id] = {}
    send_language_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text in ["Русский", "O‘zbekcha", "English"])
def language_handler(message):
    if message.text == "Русский":
        lang = "ru"
    elif message.text == "O‘zbekcha":
        lang = "uz"
    else:
        lang = "en"

    user_data[message.chat.id] = {"lang": lang}
    send_phone_request(message.chat.id, lang)


@bot.message_handler(content_types=["contact"])
def contact_handler(message):
    chat_id = message.chat.id

    if chat_id not in user_data or "lang" not in user_data[chat_id]:
        send_language_menu(chat_id)
        return

    lang = user_data[chat_id]["lang"]
    user_data[chat_id]["phone"] = message.contact.phone_number

    markup = types.ReplyKeyboardRemove()
    msg = bot.send_message(chat_id, texts[lang]["name"], reply_markup=markup)
    bot.register_next_step_handler(msg, get_name)


def get_name(message):
    chat_id = message.chat.id

    if chat_id not in user_data or "lang" not in user_data[chat_id]:
        send_language_menu(chat_id)
        return

    lang = user_data[chat_id]["lang"]
    user_data[chat_id]["name"] = message.text.strip()

    msg = bot.send_message(chat_id, texts[lang]["direction"])
    bot.register_next_step_handler(msg, get_direction)


def get_direction(message):
    chat_id = message.chat.id

    if chat_id not in user_data or "lang" not in user_data[chat_id]:
        send_language_menu(chat_id)
        return

    lang = user_data[chat_id]["lang"]
    user_data[chat_id]["direction"] = message.text.strip()

    msg = bot.send_message(chat_id, texts[lang]["group"])
    bot.register_next_step_handler(msg, get_group_number)


def get_group_number(message):
    chat_id = message.chat.id

    if chat_id not in user_data or "lang" not in user_data[chat_id]:
        send_language_menu(chat_id)
        return

    lang = user_data[chat_id]["lang"]
    user_data[chat_id]["group"] = message.text.strip()

    msg = bot.send_message(chat_id, texts[lang]["appeal"])
    bot.register_next_step_handler(msg, get_appeal)


def get_appeal(message):
    chat_id = message.chat.id

    if chat_id not in user_data or "lang" not in user_data[chat_id]:
        send_language_menu(chat_id)
        return

    lang = user_data[chat_id]["lang"]
    user_data[chat_id]["appeal"] = message.text.strip()

    data = user_data[chat_id]

    group_message = (
        "📩 Новое обращение\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🎓 Направление: {data['direction']}\n"
        f"🏫 Группа: {data['group']}\n"
        f"💬 Обращение:\n{data['appeal']}"
    )

    bot.send_message(GROUP_ID, group_message)
    bot.send_message(chat_id, texts[lang]["done"])

    user_data[chat_id] = {}
    send_language_menu(chat_id)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def fallback_handler(message):
    chat_id = message.chat.id

    if chat_id not in user_data or "lang" not in user_data[chat_id]:
        send_language_menu(chat_id)
        return

    lang = user_data[chat_id]["lang"]

    if "phone" not in user_data[chat_id]:
        send_phone_request(chat_id, lang)
        bot.send_message(chat_id, texts[lang]["phone_error"])


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        return


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


def run_bot():
    bot.infinity_polling()


if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    run_web_server()
