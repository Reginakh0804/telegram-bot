import telebot
from telebot import types

TOKEN = "8277931008:AAHYGbRNreR96KQgKXB7avGPNIKI9a--tbQ"
GROUP_ID = -4871965571

bot = telebot.TeleBot(TOKEN)

user_data = {}

# Тексты
texts = {
    "ru": {
        "start": "Пожалуйста, выберите язык:",
        "phone": "Пожалуйста, отправьте свой номер телефона.",
        "name": "Пожалуйста, введите ваше полное имя.",
        "direction": "Пожалуйста, укажите направление обучения.",
        "group": "Пожалуйста, укажите номер вашей учебной группы.",
        "message": "Пожалуйста, напишите своё обращение.",
        "done": "✅ Спасибо! Ваше обращение зарегистрировано."
    },
    "uz": {
        "start": "Iltimos, tilni tanlang:",
        "phone": "Iltimos, telefon raqamingizni yuboring.",
        "name": "Iltimos, to‘liq ism-familiyangizni kiriting.",
        "direction": "Iltimos, ta’lim yo‘nalishingizni kiriting.",
        "group": "Iltimos, o‘quv guruhingiz raqamini kiriting.",
        "message": "Iltimos, murojaatingizni yozing.",
        "done": "✅ Rahmat! Murojaatingiz ro‘yxatga olindi."
    },
    "en": {
        "start": "Please choose a language:",
        "phone": "Please share your phone number.",
        "name": "Please enter your full name.",
        "direction": "Please specify your field of study.",
        "group": "Please enter your study group number.",
        "message": "Please write your message.",
        "done": "✅ Thank you! Your request has been registered."
    }
}

# START
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Русский", "O‘zbekcha", "English")
    bot.send_message(message.chat.id, "Пожалуйста, выберите язык:", reply_markup=markup)

# ВЫБОР ЯЗЫКА
@bot.message_handler(func=lambda message: message.text in ["Русский", "O‘zbekcha", "English"])
def choose_lang(message):
    if message.text == "Русский":
        lang = "ru"
    elif message.text == "O‘zbekcha":
        lang = "uz"
    else:
        lang = "en"

    user_data[message.chat.id] = {"lang": lang}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("📱 Отправить номер", request_contact=True)
    markup.add(button)

    bot.send_message(message.chat.id, texts[lang]["phone"], reply_markup=markup)

# ПОЛУЧЕНИЕ ТЕЛЕФОНА
@bot.message_handler(content_types=['contact'])
def get_phone(message):
    chat_id = message.chat.id
    lang = user_data[chat_id]["lang"]

    user_data[chat_id]["phone"] = message.contact.phone_number

    msg = bot.send_message(chat_id, texts[lang]["name"])
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    chat_id = message.chat.id
    lang = user_data[chat_id]["lang"]

    user_data[chat_id]["name"] = message.text

    msg = bot.send_message(chat_id, texts[lang]["direction"])
    bot.register_next_step_handler(msg, get_direction)

def get_direction(message):
    chat_id = message.chat.id
    lang = user_data[chat_id]["lang"]

    user_data[chat_id]["direction"] = message.text

    msg = bot.send_message(chat_id, texts[lang]["group"])
    bot.register_next_step_handler(msg, get_group)

def get_group(message):
    chat_id = message.chat.id
    lang = user_data[chat_id]["lang"]

    user_data[chat_id]["group"] = message.text

    msg = bot.send_message(chat_id, texts[lang]["message"])
    bot.register_next_step_handler(msg, get_message)

def get_message(message):
    chat_id = message.chat.id
    lang = user_data[chat_id]["lang"]

    user_data[chat_id]["message"] = message.text

    data = user_data[chat_id]

    # Отправка в группу
    text = f"""
📩 Новое обращение

👤 Имя: {data['name']}
📱 Телефон: {data['phone']}
🎓 Направление: {data['direction']}
🏫 Группа: {data['group']}
💬 Обращение:
{data['message']}
"""

    bot.send_message(GROUP_ID, text)

    bot.send_message(chat_id, texts[lang]["done"])

    start(message)

bot.infinity_polling()
