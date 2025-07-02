import os, telebot
from typing import TypedDict, Dict, Tuple

class UserState(TypedDict):
    step: str | None          # текущий этап («name»/«phone»/«product»)
    data: Dict[str, str]      # накопленные ответы

users: Dict[Tuple[int, int], UserState] = {}     # глобальное хранилище
bot = telebot.TeleBot(os.getenv("TOKEN", ""))

@bot.message_handler(commands=['start'])
def command_start(msg):
    bot.send_message(chat_id=msg.chat.id, text='Давайте начнём опрос')


@bot.message_handler(content_types = ['text'])
def echo(msg):
    bot.send_message(msg.chat.id, msg.text)


























bot.infinity_polling()