import logging
import os
import telebot
from typing import TypedDict, Dict, Tuple
from telebot.types import Message
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot.util
from helpers import get_key

load_dotenv()

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

class UserState(TypedDict):
    step: str | None
    data: Dict[str, str]

users: Dict[Tuple[int, int], UserState] = {}
bot = telebot.TeleBot(os.getenv("TOKEN", ""))
ADMINS = os.getenv("ADMINS", "").split(sep=',')
print(ADMINS)

@bot.message_handler(commands=["start"])
def start(message: Message):
    key = get_key(message)
    if str(message.chat.id) in ADMINS:
        bot.send_message(chat_id=ADMINS[0], text='Добро пожаловать админ!')
        return
    bot.send_message(chat_id=message.chat.id, text="Давайте начнём опрос")
    users[key] = {"step": "name", "data": {}}
    bot.send_message(chat_id=message.chat.id, text="Ваше имя")
    print(message.chat.id)
@bot.message_handler(commands=["cancel"])
def cancel(message):
    key = get_key(message)
    if key in users:
        users.pop(key, None)
        bot.send_message(message.chat.id, "Опрос отменён")
    else:
        bot.send_message(message.chat.id, "Нет активного опроса для отмены")

@bot.message_handler(content_types=["text", "contact"])
def common_handler(message: Message):
    key = get_key(message)
    if key not in users:
        bot.send_message(message.chat.id, "Пожалуйста, начните новый опрос с помощью команды /start")
        return

    if users[key]['step'] == 'name':
        # Сохраняем имя пользователя
        users[key]["data"].update({'name': message.text})
        users[key]["step"] = 'phone'
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn_contact = KeyboardButton("📱 Отправить контакт", request_contact=True)
        kb.add(btn_contact)

        bot.send_message(
            message.chat.id,
            "Нажмите кнопку, чтобы отправить свой контакт",
            reply_markup=kb)

    elif users[key]['step'] == 'phone':
        # Безопасно извлекаем номер (contact или текст)
        contact = None
        if message.contact and getattr(message.contact, "phone_number", None):
            contact = message.contact.phone_number
        else:
            contact = message.text
        users[key]["data"].update({'phone': contact})
        users[key]["step"] = 'product'
        bot.send_message(message.chat.id, f"Спасибо! Ваш номер: {contact}", reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id, "Напишите, что бы вы хотели заказать")

    elif users[key]['step'] == 'product':
        product = message.text
        users[key]["data"].update({'product': product})

        # Экранируем данные для HTML
        html_text = (
        f"<b>📋 Итоги опроса:</b>\n\n"
        f"<b>Имя:</b> {users[key]['data']['name']}\n"
        f"<b>Телефон:</b> {users[key]['data']['phone']}\n"
        f"<b>Желаемый товар:</b> {users[key]['data']['product']}")

        markup = InlineKeyboardMarkup()
        btn_confirm = InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_survey")
        btn_edit = InlineKeyboardButton("✏️ Изменить имя", callback_data="edit_name")
        btn_site = InlineKeyboardButton("🌐 Открыть сайт", url="https://example.com")
        markup.add(btn_confirm, btn_edit)
        markup.add(btn_site)

        bot.send_message(message.chat.id, html_text, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ("confirm_survey", "edit_name"))
def handle_callbacks(call):
    key = get_key(call)

    if call.data == "confirm_survey":
        bot.answer_callback_query(call.id, "Спасибо за подтверждение!")
        # Берём данные пользователя (если есть) и очищаем стейт

        final_text = (
            "<b>Спасибо</b>\n\n"
            "Ваши данные подтверждены и сохранены.\n\n"
            f"<b>Имя:</b> {users[key]['data']['name']}\n"
            f"<b>Телефон:</b> {users[key]['data']['phone']}\n"
            f"<b>Товар:</b> {users[key]['data']['product']}"
        )
        bot.send_message(ADMINS[0], text=final_text, parse_mode='HTML')
        # Редактируем исходное сообщение, убирая клавиатуру
        try:
            bot.edit_message_text(final_text,
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  parse_mode="HTML")
        except Exception:
            bot.send_message(call.message.chat.id, final_text, parse_mode="HTML")

    elif call.data == "edit_name":
        bot.answer_callback_query(call.id, "Редактирование имени")
        try:
            bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=None)
        except Exception:
            pass

        # Переводим пользователя на шаг ввода имени
        users.setdefault(key, {"step": None, "data": {}})
        users[key]["step"] = "name"
        users[key]["data"].pop("name", None)

        bot.send_message(call.message.chat.id, "Хорошо. Введите, пожалуйста, новое имя:")

def main():
    me = bot.get_me()
    logger.info("Бот запущен: @%s (id=%s)", me.username, me.id)
    bot.infinity_polling()

if __name__ == "__main__":
    main()
