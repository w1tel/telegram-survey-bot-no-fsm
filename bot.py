import logging
import os, telebot
from typing import TypedDict, Dict, Tuple

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


class UserState(TypedDict):
    step: str | None  # текущий этап («name»/«phone»/«product»)
    data: Dict[str, str]  # накопленные ответы


users: Dict[Tuple[int, int], UserState] = {}  # глобальное хранилище
bot = telebot.TeleBot(os.getenv("TOKEN", ""))


@bot.message_handler(commands=["start"])
def command_start(msg):
    bot.send_message(chat_id=msg.chat.id, text="Давайте начнём опрос")
    users[(msg.chat.id, msg.from_user.id)] = {"step": "name", "data": {}}
    print(users)


@bot.message_handler(content_types=["text", "sticker"])
def echo(message):
    key = (message.chat.id, message.from_user.id)
    if key in users:
        bot.send_message(message.chat.id, "What the heeeeeeell!")
    else:
        bot.send_message(message.chat.id, "Nice my boy)")

    if message.content_type == "text":
        bot.reply_to(message, message.text)
    elif message.content_type == "sticker":
        bot.send_sticker(message.chat.id, message.sticker.file_id)


def main():
    me = bot.get_me()
    logger.info("Бот запущен: @%s (id=%s)", me.username, me.id)
    bot.infinity_polling()


if __name__ == "__main__":
    main()
