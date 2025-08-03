import logging
import os, telebot
from typing import TypedDict, Dict, Tuple
from telebot.types import Message
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
load_dotenv()


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


class UserState(TypedDict):
    step: str | None  # текущий этап («name»/«phone»/«product»)
    data: Dict[str, str]  # накопленные ответы


users: Dict[Tuple[int, int], UserState] = {}  # глобальное хранилище
bot = telebot.TeleBot(os.getenv("TOKEN", ""))


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(chat_id=message.chat.id, text="Давайте начнём опрос")
    users[(message.chat.id, message.from_user.id)] = {"step": "name", "data": {}}
    key = (message.chat.id, message.from_user.id)
    users[key]['step'] = 'name'
    bot.send_message(chat_id=message.chat.id, text="Ваше имя")

@bot.message_handler(content_types=["text", "contact"])
def common_handler(message: Message):
    key = (message.chat.id, message.from_user.id)
    if users[key]['step'] == 'name':
        users[key]["data"].update({'name': message.text})
        users[key]["step"] = 'phone'
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn_contact = KeyboardButton("📱 Отправить контакт", request_contact=True)
        kb.add(btn_contact)
        
        bot.send_message(
            message.chat.id,
            "Нажмите кнопку, чтобы отправить свой контакт",
            reply_markup=kb)
    elif users[key]["step"] == 'phone':
        contact = message.contact.phone_number
        bot.send_message(message.chat.id, f"Спасибо! Ваш номер: {contact}")
        users[key]["step"] = 'product'
        users[key]["data"].update({'phone': contact})
        bot.send_message(message.chat.id, f"Напишите чтобы вы хотели написать")
    elif users[key]["step"] == 'product':
        product = message.text
        users[key]["data"].update({'product': product})
        html_text = (
        f"<b>📋 Итоги опроса:</b>\n\n"
        f"<b>Имя:</b> {users[key]["data"]['name']}\n"
        f"<b>Телефон:</b> {users[key]["data"]['phone']}\n"
        f"<b>Желаемый товар:</b> {users[key]["data"]['product']}")
        bot.send_message(message.chat.id, html_text, parse_mode="HTML")

def main():
    me = bot.get_me()
    logger.info("Бот запущен: @%s (id=%s)", me.username, me.id)
    bot.infinity_polling()


if __name__ == "__main__":
    main()
